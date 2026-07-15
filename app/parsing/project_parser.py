from dataclasses import dataclass

from app.parsing.experience_parser import (
    calculate_duration_months,
    is_date_range_line,
    parse_date_range,
)


@dataclass(frozen=True)
class ParsedProject:
    """Structured project entry extracted from a resume."""

    name: str
    start_month: int | None
    start_year: int
    end_month: int | None
    end_year: int | None
    duration_months: int | None
    technologies: list[str]
    bullets: list[str]


def parse_technology_line(value: str) -> list[str]:
    """Parse a comma-separated project technology line."""
    return [
        technology.strip()
        for technology in value.split(",")
        if technology.strip()
    ]


def parse_projects_section(text: str) -> list[ParsedProject]:
    """Parse multiple project entries from a resume section."""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    projects: list[ParsedProject] = []
    index = 0

    while index < len(lines):
        if index + 2 >= len(lines):
            raise ValueError(
                f"Incomplete project entry near: {lines[index]}"
            )

        name = lines[index]
        date_line = lines[index + 1]
        technologies_line = lines[index + 2]

        if not is_date_range_line(date_line):
            raise ValueError(
                f"Expected date range after project '{name}', "
                f"but found: {date_line}"
            )

        date_range = parse_date_range(date_line)
        duration_months = calculate_duration_months(date_range)
        technologies = parse_technology_line(technologies_line)

        index += 3
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

        projects.append(
            ParsedProject(
                name=name,
                start_month=date_range.start_month,
                start_year=date_range.start_year,
                end_month=date_range.end_month,
                end_year=date_range.end_year,
                duration_months=duration_months,
                technologies=technologies,
                bullets=bullets,
            )
        )

    return projects