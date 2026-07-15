from pathlib import Path

import fitz
import re



class ResumeParsingError(Exception):
    """Raised when a resume PDF cannot be parsed."""


def extract_pdf_text(file_path: str | Path) -> str:
    """Extract readable text from a text-based PDF resume."""

    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Resume file not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ResumeParsingError("Only PDF files are currently supported.")

    try:
        with fitz.open(pdf_path) as document:
            pages = [
                page.get_text("text").strip()
                for page in document
            ]
    except (fitz.FileDataError, RuntimeError) as exc:
        raise ResumeParsingError(
            f"Could not read PDF: {pdf_path}"
        ) from exc

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

def clean_resume_text(text: str) -> str:
    """Normalize extracted resume text for downstream parsing."""

    # Join words split across lines with a hyphen.
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Replace repeated spaces and tabs with one space.
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces around line breaks.
    text = re.sub(r" *\n *", "\n", text)

    # Collapse three or more line breaks into two.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()