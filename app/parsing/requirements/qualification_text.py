import re


_QUALIFICATION_HEADINGS = {
    "qualifications",
    "requirements",
    "minimum qualifications",
    "basic qualifications",
    "required qualifications",
    "preferred qualifications",
    "desired qualifications",
    "preferred skills",
    "skills and experience",
    "experience and qualifications",
    "who you are",
    "what you bring",
    "what youll bring",
    "what were looking for",
    "what we are looking for",
    "ideal candidate",
    "bonus points",
    "nice to have",
    "what you need",
}


def _normalize_heading(value: str) -> str:
    """Normalize a possible Markdown heading for comparison."""

    normalized = value.strip()

    normalized = re.sub(
        r"^#{1,6}\s*",
        "",
        normalized,
    )

    normalized = normalized.strip("#*_: ")

    normalized = (
        normalized
        .replace("’", "'")
        .replace("'", "")
        .casefold()
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    return normalized.strip()


def _is_markdown_heading(value: str) -> bool:
    """Return whether a line is formatted as a Markdown heading."""

    stripped_value = value.strip()

    if re.match(
        r"^#{1,6}\s+\S",
        stripped_value,
    ):
        return True

    return bool(
        re.match(
            r"^\*\*.+\*\*:?\s*$",
            stripped_value,
        )
    )


def extract_qualification_text(
    description: str,
) -> str:
    """
    Extract qualification-focused Markdown sections.

    If no recognized qualification heading exists, return the original
    description so postings with unstructured text remain supported.
    """

    if not description.strip():
        return ""

    selected_lines: list[str] = []
    collecting = False
    found_qualification_heading = False

    for line in description.splitlines():
        normalized_heading = _normalize_heading(line)
        is_qualification_heading = (
            normalized_heading
            in _QUALIFICATION_HEADINGS
        )

        if is_qualification_heading:
            collecting = True
            found_qualification_heading = True
            selected_lines.append(line)
            continue

        if _is_markdown_heading(line):
            collecting = False
            continue

        if collecting:
            selected_lines.append(line)

    if not found_qualification_heading:
        return description.strip()

    extracted_text = "\n".join(
        selected_lines
    ).strip()

    return extracted_text or description.strip()