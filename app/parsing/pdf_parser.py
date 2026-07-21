import re
from pathlib import Path

import fitz


class ResumeParsingError(Exception):
    """Raised when a resume PDF cannot be parsed."""


def _extract_document_text(
    document: fitz.Document,
) -> str:
    """Extract and validate text from an open PDF document."""

    pages = [
        page.get_text("text").strip()
        for page in document
    ]

    extracted_text = "\n\n".join(
        page_text
        for page_text in pages
        if page_text
    ).strip()

    if not extracted_text:
        raise ResumeParsingError(
            "No readable text was found in the PDF."
        )

    return extracted_text


def extract_pdf_text(
    file_path: str | Path,
) -> str:
    """Extract readable text from a PDF stored on disk."""

    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"Resume file not found: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ResumeParsingError(
            "Only PDF files are currently supported."
        )

    try:
        with fitz.open(pdf_path) as document:
            return _extract_document_text(document)

    except ResumeParsingError:
        raise

    except (fitz.FileDataError, RuntimeError) as exc:
        raise ResumeParsingError(
            f"Could not read PDF: {pdf_path}"
        ) from exc


def extract_pdf_text_from_bytes(
    pdf_bytes: bytes,
) -> str:
    """Extract readable text from an uploaded PDF without saving it."""

    if not pdf_bytes:
        raise ResumeParsingError(
            "The uploaded PDF is empty."
        )

    try:
        with fitz.open(
            stream=pdf_bytes,
            filetype="pdf",
        ) as document:
            return _extract_document_text(document)

    except ResumeParsingError:
        raise

    except (fitz.FileDataError, RuntimeError) as exc:
        raise ResumeParsingError(
            "The uploaded file could not be read as a PDF."
        ) from exc


def clean_resume_text(text: str) -> str:
    """Normalize extracted resume text for downstream parsing."""

    text = re.sub(
        r"(\w)-\n(\w)",
        r"\1\2",
        text,
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r" *\n *",
        "\n",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()