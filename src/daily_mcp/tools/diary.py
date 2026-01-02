"""Diary tools for free-form journaling. Stored as JSON files."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path  # noqa: TC003 - used at runtime for function signatures
from typing import Any

from daily_mcp.logging import get_logger

logger = get_logger("tools.diary")


def _get_diary_file(diary_dir: Path, date: str) -> Path:
    """Get diary file path for a specific date. Format: YYYY-MM-DD.json"""
    return diary_dir / f"{date}.json"


def _load_diary(diary_dir: Path, date: str) -> list[dict[str, Any]]:
    """Load diary entries for a specific date."""
    diary_file = _get_diary_file(diary_dir, date)
    if diary_file.exists():
        with diary_file.open(encoding="utf-8") as f:
            data: list[dict[str, Any]] = json.load(f)
            return data
    return []


def _save_diary(diary_dir: Path, date: str, entries: list[dict[str, Any]]) -> None:
    """Save diary entries for a specific date."""
    diary_file = _get_diary_file(diary_dir, date)
    with diary_file.open("w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


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
    now = datetime.now()

    if datetime_str:
        # Parse provided datetime
        try:
            entry_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return f"Invalid datetime format: {datetime_str}. Use YYYY-MM-DD HH:MM:SS"
    else:
        entry_datetime = now

    diary_date = entry_datetime.strftime("%Y-%m-%d")
    logger.info("Adding diary entry for %s", entry_datetime.strftime("%Y-%m-%d %H:%M:%S"))

    entries = _load_diary(diary_dir, diary_date)
    entry: dict[str, Any] = {
        "content": content,
        "datetime": entry_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "created_at": now.isoformat(),
    }
    if tags:
        entry["tags"] = tags

    entries.append(entry)
    _save_diary(diary_dir, diary_date, entries)

    logger.debug("Diary saved to %s", _get_diary_file(diary_dir, diary_date))
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
    file_date: str,
    start_dt: datetime,
    end_dt: datetime,
    keyword: str | None,
    tag: str | None,
) -> bool:
    """Check if an entry matches the search filters."""
    # Check datetime range
    entry_dt_str = entry.get("datetime", entry.get("time", ""))
    if entry_dt_str:
        try:
            entry_dt = datetime.strptime(entry_dt_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            entry_dt = datetime.strptime(f"{file_date} {entry_dt_str}", "%Y-%m-%d %H:%M:%S")

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

        dt_str = entry.get("datetime", entry.get("time", ""))
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
    for diary_file in sorted(diary_dir.glob("*.json"), reverse=True):
        file_date = diary_file.stem
        if start_date <= file_date <= end_date:
            entries = _load_diary(diary_dir, file_date)
            for entry in entries:
                if _entry_matches_filter(entry, file_date, start_dt, end_dt, keyword, tag):
                    results.append((file_date, entry))

    logger.info("Found %d matching diary entries", len(results))
    return _format_search_results(results)
