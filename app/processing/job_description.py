import html
import re

from bs4 import BeautifulSoup


def normalize_job_description(value: str) -> str:
    """
    Convert an HTML or HTML-encoded job description into normalized text.

    Paragraph and list boundaries are preserved as line breaks while
    repeated whitespace and blank lines are removed.
    """

    decoded_value = value

    for _ in range(3):
        unescaped_value = html.unescape(decoded_value)

        if unescaped_value == decoded_value:
            break

        decoded_value = unescaped_value

    document = BeautifulSoup(
        decoded_value,
        "html.parser",
    )

    extracted_text = document.get_text(separator="\n")

    normalized_lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in extracted_text.splitlines()
    ]

    return "\n".join(
        line
        for line in normalized_lines
        if line
    )