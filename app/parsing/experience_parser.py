import re
from dataclasses import dataclass
from enum import StrEnum
from datetime import date
from collections.abc import Mapping


class EmploymentType(StrEnum):
    """Supported employment categories for parsed resume experience."""

    FULL_TIME = "full_time"
    INTERNSHIP = "internship"
    CO_OP = "co_op"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    UNKNOWN = "unknown"

MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


@dataclass(frozen=True)
class ParsedExperience:
    """Structured work-experience entry extracted from a resume."""

    company: str
    title: str
    employment_type: EmploymentType
    employment_type_confidence: float
    employment_type_reason: str

    start_month: int | None
    start_year: int
    end_month: int | None
    end_year: int | None

    duration_months: int | None
    location: str | None
    bullets: list[str]

@dataclass(frozen=True)
class ParsedDateRange:
    """Structured start and end dates extracted from a resume date range."""

    start_month: int | None
    start_year: int
    end_month: int | None
    end_year: int | None

@dataclass(frozen=True)
class EmploymentClassification:
    """Employment type inference with confidence and explanation."""

    employment_type: EmploymentType
    confidence: float
    reason: str

def parse_month_year(value: str) -> tuple[int | None, int]:
    """Parse a value such as 'May 2025' or '2025'."""

    normalized = value.strip().lower()

    year_match = re.search(r"\b(?:19|20)\d{2}\b", normalized)

    if year_match is None:
        raise ValueError(f"Could not find a year in date value: {value}")

    year = int(year_match.group())

    month: int | None = None

    for month_name, month_number in MONTHS.items():
        if re.search(
            rf"(?<![a-z]){re.escape(month_name)}(?![a-z])",
            normalized,
        ):
            month = month_number
            break

    return month, year


def parse_date_range(value: str) -> ParsedDateRange:
    """Parse a resume date range such as 'May 2025 - Sep 2025'."""

    parts = re.split(r"\s*[-–—]\s*", value.strip(), maxsplit=1)

    if len(parts) != 2:
        raise ValueError(f"Invalid date range: {value}")

    start_month, start_year = parse_month_year(parts[0])

    normalized_end = parts[1].strip().lower()

    if normalized_end in {"present", "current"}:
        today = date.today()
        end_month = today.month
        end_year = today.year
    else:
        end_month, end_year = parse_month_year(parts[1])

    return ParsedDateRange(
        start_month=start_month,
        start_year=start_year,
        end_month=end_month,
        end_year=end_year,
    )


def calculate_duration_months(date_range: ParsedDateRange) -> int | None:
    """Calculate inclusive duration in months when both months are known."""

    if (
        date_range.start_month is None
        or date_range.end_month is None
        or date_range.end_year is None
    ):
        return None

    start_total = (
        date_range.start_year * 12
        + date_range.start_month
    )

    end_total = (
        date_range.end_year * 12
        + date_range.end_month
    )

    duration = end_total - start_total + 1

    if duration <= 0:
        raise ValueError("Experience end date occurs before start date.")

    return duration


def classify_employment_type(
    title: str,
    *,
    override: EmploymentType | None = None,
) -> EmploymentClassification:
    """Classify employment type using explicit wording or a manual override."""

    if override is not None:
        return EmploymentClassification(
            employment_type=override,
            confidence=1.0,
            reason="Employment type was manually specified.",
        )

    normalized_title = title.lower()

    if "intern" in normalized_title:
        return EmploymentClassification(
            employment_type=EmploymentType.INTERNSHIP,
            confidence=1.0,
            reason="Job title explicitly contains internship language.",
        )

    if "co-op" in normalized_title or "coop" in normalized_title:
        return EmploymentClassification(
            employment_type=EmploymentType.CO_OP,
            confidence=1.0,
            reason="Job title explicitly contains co-op language.",
        )

    if "part-time" in normalized_title or "part time" in normalized_title:
        return EmploymentClassification(
            employment_type=EmploymentType.PART_TIME,
            confidence=1.0,
            reason="Job title explicitly contains part-time language.",
        )

    if "contract" in normalized_title or "contractor" in normalized_title:
        return EmploymentClassification(
            employment_type=EmploymentType.CONTRACT,
            confidence=1.0,
            reason="Job title explicitly contains contract language.",
        )

    return EmploymentClassification(
        employment_type=EmploymentType.UNKNOWN,
        confidence=0.0,
        reason="Employment type could not be determined from the job title.",
    )

DATE_RANGE_PATTERN = re.compile(
    r"^(?:[A-Za-z]{3,9}\s+)?(?:19|20)\d{2}"
    r"\s*[-–—]\s*"
    r"(?:(?:[A-Za-z]{3,9}\s+)?(?:19|20)\d{2}|Present|Current)$",
    flags=re.IGNORECASE,
)


def is_date_range_line(value: str) -> bool:
    """Return True when a line resembles a resume employment date range."""
    return DATE_RANGE_PATTERN.fullmatch(value.strip()) is not None


def parse_experience_section(
    text: str,
    *,
    employment_type_overrides: Mapping[
        tuple[str, str],
        EmploymentType,
    ] | None = None,
) -> list[ParsedExperience]:
    """Parse multiple work-experience entries from a resume section."""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    overrides = employment_type_overrides or {}
    experiences: list[ParsedExperience] = []

    index = 0

    while index < len(lines):
        if index + 3 >= len(lines):
            raise ValueError(
                "Incomplete work-experience entry near: "
                f"{lines[index]}"
            )

        company = lines[index]
        date_line = lines[index + 1]
        title = lines[index + 2]
        location = lines[index + 3]

        if not is_date_range_line(date_line):
            raise ValueError(
                f"Expected date range after company '{company}', "
                f"but found: {date_line}"
            )

        date_range = parse_date_range(date_line)
        duration_months = calculate_duration_months(date_range)

        classification = classify_employment_type(
            title,
            override=overrides.get((company, title)),
        )

        index += 4
        bullets: list[str] = []

        while index < len(lines):
            line = lines[index]

            if (
                index + 1 < len(lines)
                and is_date_range_line(lines[index + 1])
            ):
                break

            if line.startswith("•"):
                bullet = line.removeprefix("•").strip()

                if bullet:
                    bullets.append(bullet)
            elif bullets:
                bullets[-1] = f"{bullets[-1]} {line}".strip()

            index += 1

        experiences.append(
            ParsedExperience(
                company=company,
                title=title,
                employment_type=classification.employment_type,
                employment_type_confidence=classification.confidence,
                employment_type_reason=classification.reason,
                start_month=date_range.start_month,
                start_year=date_range.start_year,
                end_month=date_range.end_month,
                end_year=date_range.end_year,
                duration_months=duration_months,
                location=location,
                bullets=bullets,
            )
        )

    return experiences

