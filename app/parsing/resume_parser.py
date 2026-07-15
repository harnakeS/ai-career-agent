from dataclasses import dataclass
from pathlib import Path

from app.parsing.pdf_parser import clean_resume_text, extract_pdf_text
from app.parsing.section_parser import ResumeSections, split_resume_sections
from app.parsing.skills_parser import ParsedSkills, parse_skills_section
from app.parsing.education_parser import (
    ParsedEducation,
    parse_education_section
)
from app.parsing.experience_parser import (
    EmploymentType,
    ParsedExperience,
    parse_experience_section,
)
from app.parsing.project_parser import (
    ParsedProject,
    parse_projects_section,
)


@dataclass(frozen=True)
class ParsedResume:
    """Structured result produced from a resume PDF."""

    raw_text: str
    cleaned_text: str
    sections: ResumeSections
    skills: ParsedSkills
    education: ParsedEducation
    experiences: list[ParsedExperience]
    projects: list[ParsedProject]


def parse_resume(file_path: str | Path) -> ParsedResume:
    """Extract and structure the currently supported resume data."""

    raw_text = extract_pdf_text(file_path)
    cleaned_text = clean_resume_text(raw_text)
    sections = split_resume_sections(cleaned_text)
    skills = parse_skills_section(sections.skills)
    education = parse_education_section(sections.education)
    projects = parse_projects_section(sections.projects)
    experience_overrides = {
        (
            "Dropp Logistics",
            "WMS Solution Specialist",
        ): EmploymentType.INTERNSHIP,
    }

    experiences = parse_experience_section(
        sections.work_experience,
        employment_type_overrides=experience_overrides,
    )

    return ParsedResume(
        raw_text=raw_text,
        cleaned_text=cleaned_text,
        sections=sections,
        skills=skills,
        education=education,
        experiences=experiences,
        projects=projects,
    )