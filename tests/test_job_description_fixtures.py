import pytest

from tests.fixtures.jobs import load_job_description


@pytest.mark.parametrize(
    "relative_path",
    [
        "backend/ibm_entry_backend.txt",
        "backend/fiserv_mid_backend.txt",
        "ai/citi_ai_mid.txt",
        "cloud/amazon_cloud_mid.txt",
        "data/snowflake_data_entry.txt",
        "it/apple_it_entry.txt",
    ],
)
def test_job_description_fixture_is_not_empty(
    relative_path: str,
) -> None:
    description = load_job_description(relative_path)

    assert description.strip()
    assert len(description.split()) >= 25


def test_missing_job_description_fixture_raises_error() -> None:
    with pytest.raises(
        FileNotFoundError,
        match="Job-description fixture not found",
    ):
        load_job_description("backend/missing.txt")