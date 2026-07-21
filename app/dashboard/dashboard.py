from pathlib import Path

import streamlit as st

from app.composition import (
    create_selected_company_pipeline,
)
from app.config.company_sources import (
    CompanySourcesLoadingError,
    load_company_sources,
)
from app.dashboard.view_models import (
    company_source_to_row,
    filter_job_rows,
    job_record_to_row,
)
from app.database.database import (
    SessionLocal,
    create_database,
)
from app.database.repository import JobRepository
from app.job_sources.models import (
    CompanySourceConfiguration,
)
from app.pipeline.selected_company_pipeline import (
    SelectedCompanyRunResult,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPANY_SOURCES_PATH = (
    PROJECT_ROOT / "config" / "company_sources.json"
)


def load_configuration(
) -> CompanySourceConfiguration:
    """Load selected-company configuration for the dashboard."""

    return load_company_sources(
        COMPANY_SOURCES_PATH
    )


def load_job_rows(
    *,
    active_only: bool,
) -> list[dict[str, object]]:
    """Load persisted jobs and convert them before closing the session."""

    with SessionLocal() as session:
        repository = JobRepository(session)
        records = repository.list_jobs(
            active_only=active_only
        )

        return [
            job_record_to_row(record)
            for record in records
        ]


def display_run_result(
    result: SelectedCompanyRunResult,
) -> None:
    """Display the latest selected-company scan result."""

    st.subheader("Latest Scan")

    first_row = st.columns(4)

    first_row[0].metric(
        "Collected",
        result.collected_jobs,
    )
    first_row[1].metric(
        "New",
        result.new_jobs,
    )
    first_row[2].metric(
        "Updated",
        result.updated_jobs,
    )
    first_row[3].metric(
        "Deactivated",
        result.deactivated_jobs,
    )

    second_row = st.columns(3)

    second_row[0].metric(
        "Successful Companies",
        result.successful_collections,
    )
    second_row[1].metric(
        "Collection Failures",
        result.collection_failures,
    )
    second_row[2].metric(
        "Persistence Failures",
        result.persistence_failures,
    )

    for failure in result.collection.failures:
        st.error(
            f"{failure.company_name}: "
            f"{failure.error_type} — "
            f"{failure.message}"
        )

    for failure in result.persistence.failures:
        st.error(
            f"{failure.source.company_name}: "
            f"{failure.error_type} — "
            f"{failure.message}"
        )


def display_companies(
    configuration: CompanySourceConfiguration,
) -> None:
    """Display configured company sources."""

    st.subheader("Selected Companies")

    company_rows = [
        company_source_to_row(source)
        for source in configuration.sources
    ]

    st.dataframe(
        company_rows,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Careers": st.column_config.LinkColumn(
                "Careers",
                display_text="Open careers page",
            ),
        },
    )


def display_jobs(
    configuration: CompanySourceConfiguration,
) -> None:
    """Display stored job postings with basic filters."""

    st.subheader("Job Opportunities")

    all_rows = load_job_rows(
        active_only=False
    )

    inactive_count = sum(
        row["Status"] == "Inactive"
        for row in all_rows
    )

    include_inactive = st.checkbox(
        "Include inactive jobs",
        value=False,
        help=(
            "Inactive jobs are postings that disappeared "
            "from a successful company scan."
        ),
    )

    if include_inactive:
        rows = all_rows

        if inactive_count == 0:
            st.info(
                "No inactive job postings are currently stored."
            )
    else:
        rows = [
            row
            for row in all_rows
            if row["Status"] == "Active"
        ]

    available_companies = sorted({
        str(row["Company"])
        for row in rows
    })

    default_companies = [
        source.company_name
        for source in configuration.sources
        if (
            source.enabled
            and source.company_name
            in available_companies
        )
    ]

    filter_columns = st.columns([2, 1])

    with filter_columns[0]:
        search_query = st.text_input(
            "Search",
            placeholder=(
                "Search by title, company, or location"
            ),
        )

    with filter_columns[1]:
        selected_companies = st.multiselect(
            "Companies",
            options=available_companies,
            default=default_companies,
            help=(
                "Selected companies are shown by default. "
                "Clear the selection to display every "
                "company stored in the database."
            ),
        )

    filtered_rows = filter_job_rows(
        rows,
        query=search_query,
        companies=selected_companies,
    )

    status_label = (
        "active and inactive"
        if include_inactive
        else "active"
    )

    st.caption(
        f"Showing {len(filtered_rows)} of "
        f"{len(rows)} {status_label} stored job postings."
    )

    if not filtered_rows:
        st.info(
            "No jobs match the current filters."
        )
        return

    st.dataframe(
        filtered_rows,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Match Score": st.column_config.NumberColumn(
                "Match Score",
                format="%.1f",
            ),
            "Apply": st.column_config.LinkColumn(
                "Apply",
                display_text="View posting",
            ),
        },
    )


def main() -> None:
    """Render the AI Job Scout dashboard."""

    st.set_page_config(
        page_title="AI Job Scout",
        page_icon="🔎",
        layout="wide",
    )

    create_database()

    st.title("AI Job Scout")
    st.caption(
        "Monitor selected companies and review current "
        "job opportunities in one place."
    )

    try:
        configuration = load_configuration()
    except (
        FileNotFoundError,
        CompanySourcesLoadingError,
    ) as exc:
        st.error(
            f"Unable to load company configuration: {exc}"
        )
        st.stop()

    enabled_count = sum(
        source.enabled
        for source in configuration.sources
    )

    overview_columns = st.columns(2)

    overview_columns[0].metric(
        "Configured Companies",
        len(configuration.sources),
    )
    overview_columns[1].metric(
        "Enabled Companies",
        enabled_count,
    )

    if "last_run_result" not in st.session_state:
        st.session_state.last_run_result = None

    if st.button(
        "Scan selected companies",
        type="primary",
    ):
        with st.spinner(
            "Collecting and reconciling job postings..."
        ):
            try:
                pipeline = (
                    create_selected_company_pipeline()
                )
                result = pipeline.run(
                    configuration.sources
                )
            except Exception as exc:
                st.error(
                    f"The company scan could not complete: "
                    f"{exc}"
                )
            else:
                st.session_state.last_run_result = result
                st.success(
                    "Selected-company scan completed."
                )

    last_run_result = (
        st.session_state.last_run_result
    )

    if last_run_result is not None:
        display_run_result(last_run_result)

    st.divider()
    display_companies(configuration)

    st.divider()
    display_jobs(configuration)


if __name__ == "__main__":
    main()