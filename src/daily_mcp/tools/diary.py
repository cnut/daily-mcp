"""Diary tools for free-form journaling. Stored as Markdown files.

File structure: diary_dir/YYYY/MM/YYYY-MM-DD.md

Markdown format:
---
date: 2026-01-02
tags: [tag1, tag2]
---

## 08:30

Content here...

#tag1 #tag2

## 12:00

Another entry...
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path  # noqa: TC003 - used at runtime for function signatures
from typing import Any

from daily_mcp.logging import get_logger

logger = get_logger("tools.diary")


def _get_diary_file(diary_dir: Path, date: str) -> Path:
    """Get diary file path for a specific date. Format: YYYY/MM/YYYY-MM-DD.md"""
    year, month, _ = date.split("-")
    return diary_dir / year / month / f"{date}.md"


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter_str = parts[1].strip()
    body = parts[2].strip()

    # Simple YAML parsing for our use case
    frontmatter: dict[str, Any] = {}
    for line in frontmatter_str.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            # Parse tags list
            if key == "tags" and value.startswith("["):
                tags = re.findall(r"[\w\u4e00-\u9fff-]+", value)
                frontmatter[key] = tags
            else:
                frontmatter[key] = value

    return frontmatter, body


def _build_frontmatter(date: str, tags: list[str]) -> str:
    """Build YAML frontmatter string."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tags_str = ", ".join(tags) if tags else ""
    return f"""---
date: {date}
modification_date: {now}
tags: [{tags_str}]
---"""


def _parse_entries(body: str, file_date: str) -> list[dict[str, Any]]:
    """Parse markdown body into diary entries."""
    entries: list[dict[str, Any]] = []

    # Split by ## HH:MM headers
    pattern = r"^## (\d{2}:\d{2})(?::(\d{2}))?\s*$"
    sections = re.split(pattern, body, flags=re.MULTILINE)

    # sections[0] is content before first header (usually empty)
    # Then groups of (hour:minute, seconds_or_none, content)
    i = 1
    while i < len(sections):
        time_hm = sections[i]
        time_ss = sections[i + 1] if i + 1 < len(sections) else None
        content_block = sections[i + 2] if i + 2 < len(sections) else ""
        i += 3

        time_str = f"{time_hm}:{time_ss}" if time_ss else f"{time_hm}:00"
        content_block = content_block.strip()

        if not content_block:
            continue

        # Extract inline tags from content
        inline_tags = re.findall(r"#([\w\u4e00-\u9fff-]+)", content_block)
        # Remove inline tags from content for clean display
        clean_content = re.sub(r"\s*#[\w\u4e00-\u9fff-]+", "", content_block).strip()

        entries.append(
            {
                "datetime": f"{file_date} {time_str}",
                "content": clean_content,
                "tags": inline_tags,
            }
        )

    return entries


def _load_diary(diary_dir: Path, date: str) -> list[dict[str, Any]]:
    """Load diary entries for a specific date from markdown file."""
    diary_file = _get_diary_file(diary_dir, date)
    if not diary_file.exists():
        return []

    content = diary_file.read_text(encoding="utf-8")
    _, body = _parse_frontmatter(content)
    return _parse_entries(body, date)


def _collect_all_tags(diary_dir: Path, date: str, new_tags: list[str] | None) -> list[str]:
    """Collect all unique tags from existing entries and new tags."""
    existing_entries = _load_diary(diary_dir, date)
    all_tags: set[str] = set(new_tags or [])

    for entry in existing_entries:
        all_tags.update(entry.get("tags", []))

    return sorted(all_tags)


def _append_entry_to_markdown(
    diary_dir: Path,
    date: str,
    time_str: str,
    content: str,
    tags: list[str] | None,
) -> None:
    """Append a new entry to the markdown diary file."""
    diary_file = _get_diary_file(diary_dir, date)
    diary_file.parent.mkdir(parents=True, exist_ok=True)

    # Build inline tags string
    inline_tags = " ".join(f"#{tag}" for tag in tags) if tags else ""
    entry_block = f"\n\n## {time_str}\n\n{content}"
    if inline_tags:
        entry_block += f"\n\n{inline_tags}"

    if diary_file.exists():
        # Read existing content and update frontmatter
        existing_content = diary_file.read_text(encoding="utf-8")
        _, body = _parse_frontmatter(existing_content)

        # Collect all tags
        all_tags = _collect_all_tags(diary_dir, date, tags)

        # Rebuild file with updated frontmatter
        new_frontmatter = _build_frontmatter(date, all_tags)
        new_content = f"{new_frontmatter}\n{body}{entry_block}"
    else:
        # Create new file
        all_tags = list(tags) if tags else []
        new_frontmatter = _build_frontmatter(date, all_tags)
        new_content = f"{new_frontmatter}{entry_block}"

    diary_file.write_text(new_content, encoding="utf-8")


def add_diary(
    diary_dir: Path,
    content: str,
    tags: list[str] | None = None,
    datetime_str: str | None = None,
) -> str:
    """
    Add a diary entry.

    Args:
        diary_dir: Directory to store diary files
        content: Diary content
        tags: Optional tags for categorization
        datetime_str: Datetime in YYYY-MM-DD HH:MM:SS format, defaults to now

    Returns:
        Confirmation message
    """
    if datetime_str:
        try:
            entry_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return f"Invalid datetime format: {datetime_str}. Use YYYY-MM-DD HH:MM:SS"
    else:
        entry_datetime = datetime.now()

    diary_date = entry_datetime.strftime("%Y-%m-%d")
    time_str = entry_datetime.strftime("%H:%M")

    logger.info("Adding diary entry for %s", entry_datetime.strftime("%Y-%m-%d %H:%M:%S"))

    _append_entry_to_markdown(diary_dir, diary_date, time_str, content, tags)

    diary_file = _get_diary_file(diary_dir, diary_date)
    logger.debug("Diary saved to %s", diary_file)

    tag_info = f" [tags: {', '.join(tags)}]" if tags else ""
    return f"Diary entry added for {entry_datetime.strftime('%Y-%m-%d %H:%M:%S')}{tag_info}"


def _parse_datetime_range(
    start_datetime: str | None,
    end_datetime: str | None,
) -> tuple[datetime, datetime]:
    """Parse start and end datetime strings into datetime objects."""
    now = datetime.now()

    if not start_datetime:
        start_dt = now - timedelta(days=30)
    else:
        try:
            start_dt = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            start_dt = datetime.strptime(start_datetime, "%Y-%m-%d")

    if not end_datetime:
        end_dt = now
    else:
        try:
            end_dt = datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            end_dt = datetime.strptime(end_datetime, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59
            )

    return start_dt, end_dt


def _entry_matches_filter(
    entry: dict[str, Any],
    start_dt: datetime,
    end_dt: datetime,
    keyword: str | None,
    tag: str | None,
) -> bool:
    """Check if an entry matches the search filters."""
    # Check datetime range
    entry_dt_str = entry.get("datetime", "")
    if entry_dt_str:
        try:
            entry_dt = datetime.strptime(entry_dt_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return False

        if not (start_dt <= entry_dt <= end_dt):
            return False

    # Check keyword
    if keyword and keyword.lower() not in entry["content"].lower():
        return False

    # Check tag
    if tag:
        entry_tags = entry.get("tags", [])
        if tag.lower() not in [t.lower() for t in entry_tags]:
            return False

    return True


def _format_search_results(results: list[tuple[str, dict[str, Any]]]) -> str:
    """Format search results into output string."""
    if not results:
        return "No matching diary entries found"

    output_lines = ["Diary Entries:", ""]
    current_date: str | None = None

    for file_date, entry in results:
        if file_date != current_date:
            if current_date is not None:
                output_lines.append("")
            output_lines.append(f"Date: {file_date}")
            current_date = file_date

        dt_str = entry.get("datetime", "")
        content = entry["content"]
        tags_list = entry.get("tags", [])

        display_content = content if len(content) <= 100 else content[:100] + "..."
        tag_str = f" [{', '.join(tags_list)}]" if tags_list else ""

        if dt_str:
            display_time = dt_str.split(" ")[-1] if " " in dt_str else dt_str
            output_lines.append(f"  [{display_time}]{tag_str} {display_content}")
        else:
            output_lines.append(f"  -{tag_str} {display_content}")

    return "\n".join(output_lines)


def _iter_diary_files(diary_dir: Path, start_date: str, end_date: str):
    """Iterate over diary files in date range."""
    # Search in YYYY/MM/YYYY-MM-DD.md structure
    for md_file in sorted(diary_dir.rglob("*.md"), reverse=True):
        file_date = md_file.stem  # YYYY-MM-DD
        if start_date <= file_date <= end_date:
            yield file_date, md_file


def search_diary(
    diary_dir: Path,
    keyword: str | None = None,
    tag: str | None = None,
    start_datetime: str | None = None,
    end_datetime: str | None = None,
) -> str:
    """
    Search diary entries.

    Args:
        diary_dir: Directory containing diary files
        keyword: Keyword to search
        tag: Filter by tag
        start_datetime: Start datetime in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format
        end_datetime: End datetime in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format

    Returns:
        Search results
    """
    start_dt, end_dt = _parse_datetime_range(start_datetime, end_datetime)
    start_date = start_dt.strftime("%Y-%m-%d")
    end_date = end_dt.strftime("%Y-%m-%d")

    logger.info(
        "Searching diary from %s to %s (keyword=%s, tag=%s)",
        start_dt.strftime("%Y-%m-%d %H:%M:%S"),
        end_dt.strftime("%Y-%m-%d %H:%M:%S"),
        keyword,
        tag,
    )

    # Find matching diary entries
    results: list[tuple[str, dict[str, Any]]] = []
    for file_date, _ in _iter_diary_files(diary_dir, start_date, end_date):
        entries = _load_diary(diary_dir, file_date)
        for entry in entries:
            if _entry_matches_filter(entry, start_dt, end_dt, keyword, tag):
                results.append((file_date, entry))

    logger.info("Found %d matching diary entries", len(results))
    return _format_search_results(results)
