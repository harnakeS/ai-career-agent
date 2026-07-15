from pathlib import Path

import pytest

from app.parsing.pdf_parser import (
    ResumeParsingError,
    clean_resume_text,
    extract_pdf_text,
)


def test_clean_resume_text_joins_hyphenated_words() -> None:
    raw_text = "improved warehouse pro-\nductivity"

    cleaned_text = clean_resume_text(raw_text)

    assert cleaned_text == "improved warehouse productivity"


def test_clean_resume_text_normalizes_spacing() -> None:
    raw_text = "Python    SQL\tAzure\n\n\nMachine Learning"

    cleaned_text = clean_resume_text(raw_text)

    assert cleaned_text == "Python SQL Azure\n\nMachine Learning"


def test_extract_pdf_text_rejects_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        extract_pdf_text("data/does-not-exist.pdf")


def test_extract_pdf_text_rejects_non_pdf_file(tmp_path: Path) -> None:
    text_file = tmp_path / "resume.txt"
    text_file.write_text("Example resume")

    with pytest.raises(ResumeParsingError):
        extract_pdf_text(text_file)