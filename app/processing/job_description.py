import html
import re

from bs4 import BeautifulSoup
from bs4.element import NavigableString, PageElement, Tag


_IGNORED_ELEMENTS = {
    "script",
    "style",
    "noscript",
}

_BLOCK_ELEMENTS = {
    "article",
    "blockquote",
    "div",
    "footer",
    "header",
    "main",
    "p",
    "section",
}


def _render_children(element: Tag) -> str:
    """Render all direct children of one HTML element."""

    return "".join(
        _render_node(child)
        for child in element.children
    )


def _render_list(element: Tag) -> str:
    """Convert an HTML list into Markdown-style list items."""

    list_items = element.find_all(
        "li",
        recursive=False,
    )

    rendered_items: list[str] = []

    for index, item in enumerate(list_items, start=1):
        content = _render_children(item).strip()

        if not content:
            continue

        content_lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

        if not content_lines:
            continue

        prefix = (
            f"{index}. "
            if element.name == "ol"
            else "- "
        )

        rendered_items.append(
            f"{prefix}{content_lines[0]}"
        )

        rendered_items.extend(
            f"  {line}"
            for line in content_lines[1:]
        )

    if not rendered_items:
        return ""

    return (
        "\n\n"
        + "\n".join(rendered_items)
        + "\n\n"
    )


def _render_node(node: PageElement) -> str:
    """Convert one HTML node into readable Markdown-style text."""

    if isinstance(node, NavigableString):
        return str(node)

    if not isinstance(node, Tag):
        return ""

    element_name = node.name.lower()

    if element_name in _IGNORED_ELEMENTS:
        return ""

    if element_name == "br":
        return "\n"

    if element_name == "hr":
        return "\n\n---\n\n"

    if element_name in {"ul", "ol"}:
        return _render_list(node)

    content = _render_children(node)

    if element_name in {"h1", "h2"}:
        return f"\n\n### {content.strip()}\n\n"

    if element_name in {"h3", "h4", "h5", "h6"}:
        return f"\n\n#### {content.strip()}\n\n"

    if element_name in {"strong", "b"}:
        normalized_content = content.strip()

        return (
            f"**{normalized_content}**"
            if normalized_content
            else ""
        )

    if element_name in {"em", "i"}:
        normalized_content = content.strip()

        return (
            f"*{normalized_content}*"
            if normalized_content
            else ""
        )

    if element_name == "a":
        link_text = content.strip()
        link_url = node.get("href")

        if (
            link_text
            and isinstance(link_url, str)
            and link_url.startswith(
                ("https://", "http://")
            )
        ):
            return f"[{link_text}]({link_url})"

        return link_text

    if element_name == "blockquote":
        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

        return (
            "\n\n"
            + "\n".join(
                f"> {line}"
                for line in lines
            )
            + "\n\n"
        )

    if element_name in _BLOCK_ELEMENTS:
        normalized_content = content.strip()

        return (
            f"\n\n{normalized_content}\n\n"
            if normalized_content
            else ""
        )

    return content


def _normalize_rendered_lines(value: str) -> str:
    """Normalize whitespace while preserving meaningful blank lines."""

    normalized_lines: list[str] = []

    for raw_line in value.splitlines():
        line = re.sub(
            r"[ \t]+",
            " ",
            raw_line,
        ).strip()

        if line:
            normalized_lines.append(line)
            continue

        if (
            normalized_lines
            and normalized_lines[-1] != ""
        ):
            normalized_lines.append("")

    while (
        normalized_lines
        and normalized_lines[-1] == ""
    ):
        normalized_lines.pop()

    return "\n".join(normalized_lines)


def normalize_job_description(value: str) -> str:
    """
    Convert an HTML or HTML-encoded job description into safe Markdown.

    Paragraphs, headings, lists, emphasis, links, and line breaks are
    retained without exposing provider HTML directly to the frontend.
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

    rendered_value = "".join(
        _render_node(child)
        for child in document.children
    )

    return _normalize_rendered_lines(
        rendered_value
    )