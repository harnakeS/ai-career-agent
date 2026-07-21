from collections.abc import Collection
from app.models.candidate import CandidateProfile
from app.database.models import JobRecord
from app.job_sources.models import CompanySource


JobTableRow = dict[str, object]
CompanyTableRow = dict[str, object]
JobDetail = dict[str, object]
CandidateProfileSummary = dict[str, object]


def job_record_to_row(
    record: JobRecord,
) -> JobTableRow:
    """Convert a stored job into frontend-friendly table data."""

    return {
        "Job ID": record.id,
        "Company": record.company,
        "Company": record.company,
        "Title": record.title,
        "Location": (
            record.location or "Not specified"
        ),
        "Posted": (
            record.date_posted.isoformat()
            if record.date_posted is not None
            else "Unknown"
        ),
        "Discovered": (
            record.date_discovered.date().isoformat()
        ),
        "Status": (
            "Active"
            if record.is_active
            else "Inactive"
        ),
        "Match Score": record.match_score,
        "Application Status": (
            record.application_status
            or "Not applied"
        ),
        "Apply": record.application_url,
    }

def job_record_to_detail(
    record: JobRecord,
) -> JobDetail:
    """Convert a stored job into a frontend-friendly detail view."""

    return {
        "Job ID": record.id,
        "Company": record.company,
        "Requisition ID": record.requisition_id,
        "Title": record.title,
        "Location": (
            record.location or "Not specified"
        ),
        "Description": record.description,
        "Posted": (
            record.date_posted.isoformat()
            if record.date_posted is not None
            else "Unknown"
        ),
        "Discovered": (
            record.date_discovered.date().isoformat()
        ),
        "Last Seen": (
            record.last_seen.date().isoformat()
        ),
        "Status": (
            "Active"
            if record.is_active
            else "Inactive"
        ),
        "Match Score": record.match_score,
        "Application Status": (
            record.application_status
            or "Not applied"
        ),
        "Application URL": record.application_url,
    }


def company_source_to_row(
    source: CompanySource,
) -> CompanyTableRow:
    """Convert company configuration into table data."""

    return {
        "Company": source.company_name,
        "Provider": source.provider.value.title(),
        "Status": (
            "Enabled"
            if source.enabled
            else "Disabled"
        ),
        "Careers": str(source.careers_url),
    }


def filter_job_rows(
    rows: list[JobTableRow],
    *,
    query: str = "",
    companies: Collection[str] | None = None,
) -> list[JobTableRow]:
    """Filter job rows using company selection and free-text search."""

    normalized_query = query.casefold().strip()
    selected_companies = set(companies or [])

    filtered_rows: list[JobTableRow] = []

    for row in rows:
        company = str(row["Company"])

        if (
            selected_companies
            and company not in selected_companies
        ):
            continue

        searchable_text = " ".join([
            str(row["Company"]),
            str(row["Title"]),
            str(row["Location"]),
        ]).casefold()

        if (
            normalized_query
            and normalized_query not in searchable_text
        ):
            continue

        filtered_rows.append(row)

    return filtered_rows

def candidate_profile_to_summary(
    profile: CandidateProfile,
) -> CandidateProfileSummary:
    """Convert a candidate profile into dashboard summary data."""

    technical_skills = list(dict.fromkeys([
        *profile.programming_languages,
        *profile.frameworks,
        *profile.tools,
        *profile.skills,
    ]))

    fields_of_study = [
        *profile.majors,
        *profile.minors,
    ]

    total_experience_months = sum([
        profile.full_time_experience_months,
        profile.internship_experience_months,
        profile.co_op_experience_months,
        profile.part_time_experience_months,
        profile.contract_experience_months,
    ])

    return {
        "Name": profile.name,
        "Graduation Year": (
            profile.graduation_year
            if profile.graduation_year is not None
            else "Unknown"
        ),
        "Education": profile.education,
        "Fields of Study": (
            ", ".join(fields_of_study)
            if fields_of_study
            else "Not specified"
        ),
        "Technical Skills": (
            ", ".join(technical_skills)
            if technical_skills
            else "None detected"
        ),
        "Certifications": (
            ", ".join(profile.certifications)
            if profile.certifications
            else "None detected"
        ),
        "Experience Months": total_experience_months,
        "Target Roles": (
            ", ".join(profile.desired_roles)
            if profile.desired_roles
            else "Not specified"
        ),
        "Preferred Locations": (
            ", ".join(profile.preferred_locations)
        ),
        "Relocation": (
            "Willing to relocate"
            if profile.willing_to_relocate
            else "Not willing to relocate"
        ),
        "Work Authorization": (
            "U.S. citizen"
            if profile.us_citizen
            else "Requires review"
        ),
    }