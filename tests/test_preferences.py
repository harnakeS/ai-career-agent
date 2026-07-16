import json
from pathlib import Path

import pytest

from app.config.preferences import (
    PreferencesLoadingError,
    load_candidate_preferences,
)


def test_load_candidate_preferences_reads_valid_json(
    tmp_path: Path,
) -> None:
    preferences_path = tmp_path / "preferences.json"

    preferences_path.write_text(
        json.dumps(
            {
                "preferred_locations": [
                    "New Jersey",
                    "New York",
                    "Remote",
                ],
                "willing_to_relocate": True,
                "us_citizen": True,
            }
        ),
        encoding="utf-8",
    )

    preferences = load_candidate_preferences(preferences_path)

    assert preferences.preferred_locations == [
        "New Jersey",
        "New York",
        "Remote",
    ]
    assert preferences.willing_to_relocate
    assert preferences.us_citizen


def test_load_candidate_preferences_rejects_missing_file() -> None:
    with pytest.raises(
        FileNotFoundError,
        match="Preferences file not found",
    ):
        load_candidate_preferences(
            "config/does-not-exist.json"
        )


def test_load_candidate_preferences_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    preferences_path = tmp_path / "preferences.json"
    preferences_path.write_text(
        "{invalid json",
        encoding="utf-8",
    )

    with pytest.raises(
        PreferencesLoadingError,
        match="contains invalid JSON",
    ):
        load_candidate_preferences(preferences_path)


def test_load_candidate_preferences_rejects_missing_fields(
    tmp_path: Path,
) -> None:
    preferences_path = tmp_path / "preferences.json"

    preferences_path.write_text(
        json.dumps(
            {
                "preferred_locations": [
                    "New Jersey",
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        PreferencesLoadingError,
        match="contains invalid data",
    ):
        load_candidate_preferences(preferences_path)