from pathlib import Path
from app.models.job import JobPosting

import streamlit as st

from app.composition import (
    create_selected_company_pipeline,
)
from app.config.company_sources import (
    CompanySourcesLoadingError,
    load_company_sources,
)
from app.dashboard.view_models import (
    candidate_profile_to_summary,
    company_source_to_row,
    filter_job_rows,
    job_record_to_row,
    job_record_to_detail,
    requirement_match_to_row,
    description_overlap_to_row,
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
from app.candidate.service import (
    CandidateResumeResult,
    CandidateResumeService,
)
from app.config.preferences import (
    PreferencesLoadingError,
    load_candidate_preferences,
)
from app.parsing.pdf_parser import (
    ResumeParsingError,
)
from app.composition import (
    create_candidate_job_match_service,
    create_selected_company_pipeline,
)
from app.config.ai import (
    AIConfigurationError,
    AIProvider,
    load_ai_configuration,
)
from app.database.converter import (
    job_record_to_posting,
)
from app.matching.service import (
    CandidateJobMatchResult,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPANY_SOURCES_PATH = (
    PROJECT_ROOT / "config" / "company_sources.json"
)
PREFERENCES_PATH = (
    PROJECT_ROOT / "config" / "preferences.json"
)
ENV_PATH = PROJECT_ROOT / ".env"

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

def load_job_detail(
    job_id: int,
) -> dict[str, object] | None:
    """Load one stored job and convert it before closing the session."""

    with SessionLocal() as session:
        repository = JobRepository(session)
        record = repository.get_by_id(job_id)

        if record is None:
            return None

        return job_record_to_detail(record)

def load_job_posting(
    job_id: int,
) -> JobPosting | None:
    """Load one stored job as the canonical job model."""

    with SessionLocal() as session:
        repository = JobRepository(session)
        record = repository.get_by_id(job_id)

        if record is None:
            return None

        return job_record_to_posting(record)

def display_candidate_job_match(
    result: CandidateJobMatchResult,
) -> None:
    """Display an explainable candidate-to-job match result."""

    st.markdown("#### Candidate Match")

    if result.requirements_cache_hit:
        st.caption(
            "Requirement source: SQLite cache. "
            "Ollama was not invoked for this analysis."
        )
    else:
        st.caption(
            "Requirement source: New AI extraction. "
            "The structured requirements were saved for reuse."
        )

    metrics = st.columns(5)

    metrics[0].metric(
        "Extracted Requirements",
        len(result.requirements.requirements),
    )
    metrics[1].metric(
        "Matched",
        result.matched_count,
    )
    metrics[2].metric(
        "Required Gaps",
        result.required_gap_count,
    )
    metrics[3].metric(
        "Preferred / Optional",
        result.non_required_missing_count,
    )
    metrics[4].metric(
        "Not Evaluated",
        result.unevaluated_count,
    )

    st.caption(
        "This is evidence coverage, not a final job-match score. "
        "Required gaps are missing mandatory qualifications. "
        "Preferred or optional qualifications do not determine "
        "basic eligibility. Not evaluated means the deterministic "
        "matcher does not yet support that requirement category."
    )

    overlap_rows = [
        description_overlap_to_row(overlap)
        for overlap in result.description_overlaps.overlaps
    ]

    st.markdown("##### Explicit Resume Overlap")

    st.caption(
        f"{result.overlap_count} candidate evidence item(s) "
        "appear explicitly in the job description. "
        "These overlaps are deterministic and do not depend on "
        "the AI requirement extractor. An overlap does not by "
        "itself prove that a complete job requirement is satisfied."
    )

    if overlap_rows:
        st.dataframe(
            overlap_rows,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Resume Evidence": (
                    st.column_config.TextColumn(
                        "Resume Evidence",
                        width="medium",
                    )
                ),
                "Explanation": (
                    st.column_config.TextColumn(
                        "Explanation",
                        width="large",
                    )
                ),
            },
        )
    else:
        st.info(
            "No candidate evidence was found explicitly in "
            "this job description."
        )

    st.markdown("##### Extracted Requirement Coverage")

    rows = [
        requirement_match_to_row(match)
        for match in result.evidence_matches.matches
    ]

    if not rows:
        st.info(
            "The extractor did not identify explicit requirements "
            "in this posting."
        )
        return

    st.dataframe(
        rows,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Explanation": st.column_config.TextColumn(
                "Explanation",
                width="large",
            ),
            "Supporting Evidence": (
                st.column_config.TextColumn(
                    "Supporting Evidence",
                    width="large",
                )
            ),
        },
    )


def display_job_match_analysis(
    job_id: int,
    candidate_resume: CandidateResumeResult | None,
) -> None:
    """Display controls and results for one selected job."""

    st.markdown("#### Personalized Analysis")

    if candidate_resume is None:
        st.info(
            "Upload and process a resume to analyze this job."
        )
        return

    try:
        ai_configuration = load_ai_configuration(
            env_file=ENV_PATH
        )
    except AIConfigurationError as exc:
        st.warning(
            f"AI matching is not configured correctly: {exc}"
        )
        return

    if ai_configuration.provider == AIProvider.DISABLED:
        st.info(
            "AI requirement extraction is currently disabled. "
            "Set AI_PROVIDER in your local .env file to "
            "openai or ollama to analyze this job."
        )
        return

    st.caption(
        f"Provider: {ai_configuration.provider.value.title()} "
        f"· Model: {ai_configuration.model}"
    )

    if "candidate_job_matches" not in st.session_state:
        st.session_state.candidate_job_matches = {}

    if st.button(
        "Analyze match",
        type="primary",
        key=f"analyze_job_{job_id}",
    ):
        with st.spinner(
            "Extracting requirements and matching resume evidence..."
        ):
            try:
                job = load_job_posting(job_id)

                if job is None:
                    raise ValueError(
                        "The selected job could not be found."
                    )

                service = (
                    create_candidate_job_match_service(
                        ai_configuration
                    )
                )

                result = service.match(
                    job,
                    candidate_resume.evidence,
                )

            except Exception as exc:
                st.error(
                    "The match analysis could not be completed: "
                    f"{exc}"
                )

            else:
                st.session_state.candidate_job_matches[
                    job_id
                ] = result
                if result.requirements_cache_hit:
                    st.success(
                        "Candidate match analysis completed "
                        "using cached job requirements."
                    )
                else:
                    st.success(
                        "Candidate match analysis completed. "
                        "The extracted requirements were cached."
                    )

    result = st.session_state.candidate_job_matches.get(
        job_id
    )

    if result is not None:
        display_candidate_job_match(result)


def display_job_detail(
    detail: dict[str, object],
    candidate_resume: CandidateResumeResult | None,
) -> None:
    """Display complete information for one selected job."""

    st.divider()
    st.subheader("Job Details")

    display_job_match_analysis(
        int(detail["Job ID"]),
        candidate_resume,
    )

    st.divider()

    st.markdown(
        f"### {detail['Title']}"
    )
    st.caption(
        f"{detail['Company']} · {detail['Location']}"
    )

    detail_columns = st.columns(4)

    detail_columns[0].metric(
        "Status",
        detail["Status"],
    )
    detail_columns[1].metric(
        "Posted",
        detail["Posted"],
    )
    detail_columns[2].metric(
        "Match Score",
        (
            detail["Match Score"]
            if detail["Match Score"] is not None
            else "Not scored"
        ),
    )
    detail_columns[3].metric(
        "Application Status",
        detail["Application Status"],
    )

    st.write(
        f"**Requisition ID:** "
        f"{detail['Requisition ID']}"
    )
    st.write(
        f"**Discovered:** {detail['Discovered']}"
    )
    st.write(
        f"**Last seen:** {detail['Last Seen']}"
    )

    st.link_button(
        "Open official application",
        str(detail["Application URL"]),
    )

    st.markdown("#### Job Description")
    st.markdown(str(detail["Description"]))

def display_resume_upload(
) -> CandidateResumeResult | None:
    """Process and retain a resume in the current Streamlit session."""

    st.sidebar.header("Candidate Resume")
    st.sidebar.caption(
        "Your resume is processed in memory and is not "
        "saved to the job database."
    )

    uploaded_resume = st.sidebar.file_uploader(
        "Upload resume",
        type=["pdf"],
        accept_multiple_files=False,
        help="Upload a text-based PDF resume.",
    )

    if "candidate_resume_result" not in st.session_state:
        st.session_state.candidate_resume_result = None

    if "candidate_resume_filename" not in st.session_state:
        st.session_state.candidate_resume_filename = None

    if uploaded_resume is not None:
        process_resume = st.sidebar.button(
            "Process resume",
            type="primary",
            key="process_candidate_resume",
        )

        if process_resume:
            with st.spinner(
                "Parsing resume and building candidate evidence..."
            ):
                try:
                    preferences = (
                        load_candidate_preferences(
                            PREFERENCES_PATH
                        )
                    )

                    result = (
                        CandidateResumeService().process(
                            uploaded_resume.getvalue(),
                            preferences,
                        )
                    )

                except (
                    FileNotFoundError,
                    PreferencesLoadingError,
                    ResumeParsingError,
                    ValueError,
                ) as exc:
                    st.sidebar.error(
                        f"Resume processing failed: {exc}"
                    )

                else:
                    st.session_state.candidate_resume_result = (
                        result
                    )
                    st.session_state.candidate_resume_filename = (
                        uploaded_resume.name
                    )
                    st.sidebar.success(
                        "Resume processed successfully."
                    )

                st.session_state.candidate_job_matches = {}

    result = st.session_state.candidate_resume_result
    filename = st.session_state.candidate_resume_filename

    if result is not None:
        st.sidebar.success(
            f"Active resume: {filename}"
        )

        if st.sidebar.button(
            "Clear processed resume",
            key="clear_candidate_resume",
        ):
            st.session_state.candidate_resume_result = None
            st.session_state.candidate_resume_filename = None
            st.session_state.candidate_job_matches = {}
            st.rerun()

    return result


def display_candidate_summary(
    result: CandidateResumeResult,
) -> None:
    """Display candidate information extracted from the active resume."""

    summary = candidate_profile_to_summary(
        result.profile
    )

    st.subheader("Candidate Profile")

    summary_columns = st.columns(4)

    summary_columns[0].metric(
        "Candidate",
        summary["Name"],
    )
    summary_columns[1].metric(
        "Graduation Year",
        summary["Graduation Year"],
    )
    summary_columns[2].metric(
        "Experience",
        f"{summary['Experience Months']} months",
    )
    summary_columns[3].metric(
        "Evidence Items",
        len(result.evidence.evidence),
    )

    with st.expander(
        "View parsed candidate information",
        expanded=False,
    ):
        st.write(
            f"**Education:** {summary['Education']}"
        )
        st.write(
            f"**Fields of study:** "
            f"{summary['Fields of Study']}"
        )
        st.write(
            f"**Technical skills:** "
            f"{summary['Technical Skills']}"
        )
        st.write(
            f"**Certifications:** "
            f"{summary['Certifications']}"
        )
        st.write(
            f"**Target roles:** "
            f"{summary['Target Roles']}"
        )
        st.write(
            f"**Preferred locations:** "
            f"{summary['Preferred Locations']}"
        )
        st.write(
            f"**Relocation:** {summary['Relocation']}"
        )
        st.write(
            f"**Work authorization:** "
            f"{summary['Work Authorization']}"
        )


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
    candidate_resume: CandidateResumeResult | None,
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

    table_event = st.dataframe(
        filtered_rows,
        hide_index=True,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
        key="job_opportunities_table",
        column_config={
            "Job ID": None,
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

    selected_rows = table_event.selection.rows

    if not selected_rows:
        st.caption(
            "Select a row to view the complete job description."
        )
        return

    selected_index = selected_rows[0]
    selected_job_id = int(
        filtered_rows[selected_index]["Job ID"]
    )
    detail = load_job_detail(selected_job_id)

    if detail is None:
        st.warning(
            "The selected job could not be found. "
            "Refresh the dashboard and try again."
        )
        return

    display_job_detail(
    detail,
    candidate_resume,
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

    candidate_resume = display_resume_upload()

    if candidate_resume is not None:
        st.divider()
        display_candidate_summary(
            candidate_resume
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
    display_jobs(
    configuration,
    candidate_resume,
)


if __name__ == "__main__":
    main()