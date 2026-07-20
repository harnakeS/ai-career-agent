import re


def normalize_vocabulary_text(value: str) -> str:
    """
    Apply generic text normalization without applying concept knowledge.

    This handles formatting differences while preserving characters that are
    meaningful in technical terms such as C++, C#, and Node.js.
    """

    normalized = value.casefold()

    normalized = normalized.replace("’", "'")
    normalized = normalized.replace("&", " and ")
    normalized = normalized.replace("-", " ")
    normalized = normalized.replace("_", " ")
    normalized = normalized.replace("'", "")

    normalized = re.sub(
        r"[^a-z0-9+#.\s]",
        " ",
        normalized,
    )
    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    return normalized.strip().strip(".")