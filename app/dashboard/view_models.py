from collections.abc import Collection

from app.database.models import JobRecord
from app.job_sources.models import CompanySource


JobTableRow = dict[str, object]
CompanyTableRow = dict[str, object]


def job_record_to_row(
    record: JobRecord,
) -> JobTableRow:
    """Convert a stored job into frontend-friendly table data."""

    return {
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