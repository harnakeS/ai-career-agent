from dataclasses import dataclass


@dataclass(frozen=True)
class ResumeSections:
    """Structured top-level sections extracted from resume text."""

    header: str
    education: str
    skills: str
    work_experience: str
    projects: str


SECTION_HEADINGS = [
    "EDUCATION",
    "SKILLS",
    "WORK EXPERIENCE",
    "PROJECTS",
]


def split_resume_sections(text: str) -> ResumeSections:
    """Split cleaned resume text into its main sections."""

    positions: dict[str, int] = {}

    for heading in SECTION_HEADINGS:
        position = text.find(f"\n{heading}\n")

        if position == -1 and text.startswith(f"{heading}\n"):
            position = 0

        if position != -1:
            positions[heading] = position

    missing_sections = [
        heading
        for heading in SECTION_HEADINGS
        if heading not in positions
    ]

    if missing_sections:
        missing = ", ".join(missing_sections)
        raise ValueError(f"Missing resume sections: {missing}")

    ordered_headings = sorted(
        positions,
        key=positions.get,
    )

    section_text: dict[str, str] = {}

    first_heading = ordered_headings[0]
    header_end = positions[first_heading]
    header = text[:header_end].strip()

    for index, heading in enumerate(ordered_headings):
        start = positions[heading] + len(heading) + 2

        if index + 1 < len(ordered_headings):
            next_heading = ordered_headings[index + 1]
            end = positions[next_heading]
        else:
            end = len(text)

        section_text[heading] = text[start:end].strip()

    return ResumeSections(
        header=header,
        education=section_text["EDUCATION"],
        skills=section_text["SKILLS"],
        work_experience=section_text["WORK EXPERIENCE"],
        projects=section_text["PROJECTS"],
    )