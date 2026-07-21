import json
from pathlib import Path

from pydantic import ValidationError

from app.job_sources.models import (
    CompanySourceConfiguration,
)


class CompanySourcesLoadingError(Exception):
    """Raised when company sources cannot be loaded."""


def load_company_sources(
    file_path: str | Path,
) -> CompanySourceConfiguration:
    """Load and validate selected company sources from JSON."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Company-sources file not found: {path}"
        )

    try:
        raw_data = json.loads(
            path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        raise CompanySourcesLoadingError(
            f"Company-sources file contains invalid JSON: "
            f"{path}"
        ) from exc

    try:
        return CompanySourceConfiguration.model_validate(
            raw_data
        )
    except ValidationError as exc:
        raise CompanySourcesLoadingError(
            f"Company-sources file contains invalid data: "
            f"{path}"
        ) from exc