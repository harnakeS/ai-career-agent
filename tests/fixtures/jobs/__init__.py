from pathlib import Path


FIXTURE_DIRECTORY = Path(__file__).parent


def load_job_description(relative_path: str) -> str:
    """Load a job-description fixture using a path relative to jobs/."""

    fixture_path = FIXTURE_DIRECTORY / relative_path

    if not fixture_path.is_file():
        raise FileNotFoundError(
            f"Job-description fixture not found: {relative_path}"
        )

    return fixture_path.read_text(encoding="utf-8")