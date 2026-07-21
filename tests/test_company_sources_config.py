import json
from pathlib import Path

import pytest

from app.config.company_sources import (
    CompanySourcesLoadingError,
    load_company_sources,
)
from app.job_sources.models import JobSourceProvider


def write_configuration(
    path: Path,
    sources: list[dict[str, object]],
) -> None:
    path.write_text(
        json.dumps({
            "sources": sources,
        }),
        encoding="utf-8",
    )


def create_source_data(
    *,
    company_name: str = "Example Company",
    provider: str = "greenhouse",
    source_identifier: str = "example-company",
    enabled: bool = True,
) -> dict[str, object]:
    return {
        "company_name": company_name,
        "provider": provider,
        "source_identifier": source_identifier,
        "careers_url": "https://example.com/careers",
        "enabled": enabled,
    }


def test_loads_valid_company_sources(
    tmp_path: Path,
) -> None:
    configuration_path = (
        tmp_path / "company_sources.json"
    )
    write_configuration(
        configuration_path,
        sources=[
            create_source_data(),
        ],
    )

    configuration = load_company_sources(
        configuration_path
    )

    assert len(configuration.sources) == 1

    source = configuration.sources[0]

    assert source.company_name == "Example Company"
    assert (
        source.provider
        == JobSourceProvider.GREENHOUSE
    )
    assert source.source_identifier == "example-company"
    assert source.enabled is True


def test_preserves_disabled_company_source(
    tmp_path: Path,
) -> None:
    configuration_path = (
        tmp_path / "company_sources.json"
    )
    write_configuration(
        configuration_path,
        sources=[
            create_source_data(enabled=False),
        ],
    )

    configuration = load_company_sources(
        configuration_path
    )

    assert configuration.sources[0].enabled is False


def test_rejects_missing_configuration_file() -> None:
    with pytest.raises(
        FileNotFoundError,
        match="Company-sources file not found",
    ):
        load_company_sources(
            "config/does-not-exist.json"
        )


def test_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    configuration_path = (
        tmp_path / "company_sources.json"
    )
    configuration_path.write_text(
        "{invalid json",
        encoding="utf-8",
    )

    with pytest.raises(
        CompanySourcesLoadingError,
        match="contains invalid JSON",
    ):
        load_company_sources(configuration_path)


def test_rejects_unknown_provider(
    tmp_path: Path,
) -> None:
    configuration_path = (
        tmp_path / "company_sources.json"
    )
    write_configuration(
        configuration_path,
        sources=[
            create_source_data(
                provider="unknown-provider"
            ),
        ],
    )

    with pytest.raises(
        CompanySourcesLoadingError,
        match="contains invalid data",
    ):
        load_company_sources(configuration_path)


def test_rejects_empty_source_list(
    tmp_path: Path,
) -> None:
    configuration_path = (
        tmp_path / "company_sources.json"
    )
    write_configuration(
        configuration_path,
        sources=[],
    )

    with pytest.raises(
        CompanySourcesLoadingError,
        match="contains invalid data",
    ):
        load_company_sources(configuration_path)


def test_rejects_duplicate_provider_identifier(
    tmp_path: Path,
) -> None:
    configuration_path = (
        tmp_path / "company_sources.json"
    )
    write_configuration(
        configuration_path,
        sources=[
            create_source_data(
                company_name="First Name",
                source_identifier="same-board",
            ),
            create_source_data(
                company_name="Second Name",
                source_identifier="SAME-BOARD",
            ),
        ],
    )

    with pytest.raises(
        CompanySourcesLoadingError,
        match="contains invalid data",
    ):
        load_company_sources(configuration_path)