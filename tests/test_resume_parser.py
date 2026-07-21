from pathlib import Path

import pytest
import fitz

from app.parsing.pdf_parser import (
    ResumeParsingError,
    clean_resume_text,
    extract_pdf_text,
    extract_pdf_text_from_bytes,
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

def create_pdf_bytes(
    text: str | None = None,
) -> bytes:
    document = fitz.open()
    page = document.new_page()

    if text is not None:
        page.insert_text(
            (72, 72),
            text,
        )

    pdf_bytes = document.tobytes()
    document.close()

    return pdf_bytes


def test_extracts_text_from_pdf_bytes() -> None:
    result = extract_pdf_text_from_bytes(
        create_pdf_bytes(
            "Harnake Sahi\nPython Java SQL"
        )
    )

    assert "Harnake Sahi" in result
    assert "Python Java SQL" in result


def test_rejects_empty_pdf_bytes() -> None:
    with pytest.raises(
        ResumeParsingError,
        match="uploaded PDF is empty",
    ):
        extract_pdf_text_from_bytes(b"")


def test_rejects_uploaded_pdf_without_readable_text() -> None:
    with pytest.raises(
        ResumeParsingError,
        match="No readable text",
    ):
        extract_pdf_text_from_bytes(
            create_pdf_bytes()
        )