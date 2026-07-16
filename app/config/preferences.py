import json
from pathlib import Path

from pydantic import ValidationError

from app.models.preferences import CandidatePreferences


class PreferencesLoadingError(Exception):
    """Raised when candidate preferences cannot be loaded."""


def load_candidate_preferences(
    file_path: str | Path,
) -> CandidatePreferences:
    """Load and validate candidate preferences from a JSON file."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Preferences file not found: {path}"
        )

    try:
        raw_data = json.loads(
            path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        raise PreferencesLoadingError(
            f"Preferences file contains invalid JSON: {path}"
        ) from exc

    try:
        return CandidatePreferences.model_validate(raw_data)
    except ValidationError as exc:
        raise PreferencesLoadingError(
            f"Preferences file contains invalid data: {path}"
        ) from exc