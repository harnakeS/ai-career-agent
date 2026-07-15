from dataclasses import dataclass
from pathlib import Path

from app.resume.pdf_parser import clean_resume_text, extract_pdf_text
from app.resume.section_parser import ResumeSections, split_resume_sections
from app.resume.skills_parser import ParsedSkills, parse_skills_section


@dataclass(frozen=True)
class ParsedResume:
    """Structured result produced from a resume PDF."""

    raw_text: str
    cleaned_text: str
    sections: ResumeSections
    skills: ParsedSkills


def parse_resume(file_path: str | Path) -> ParsedResume:
    """Extract and structure the currently supported resume data."""

    raw_text = extract_pdf_text(file_path)
    cleaned_text = clean_resume_text(raw_text)
    sections = split_resume_sections(cleaned_text)
    skills = parse_skills_section(sections.skills)

    return ParsedResume(
        raw_text=raw_text,
        cleaned_text=cleaned_text,
        sections=sections,
        skills=skills,
    )