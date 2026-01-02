"""Daily log tools for free-form journaling. Stored as JSON files."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from daily_mcp.logging import get_logger

if TYPE_CHECKING:
    from daily_mcp.db import Database

logger = get_logger("tools.daily_log")


def _get_log_dir() -> Path:
    """Get the daily log directory."""
    log_dir = Path.home() / ".daily-mcp" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def _get_log_file(date: str) -> Path:
    """Get log file path for a specific date. Format: YYYY-MM-DD.json"""
    return _get_log_dir() / f"{date}.json"


def _load_log(date: str) -> list[dict[str, Any]]:
    """Load logs for a specific date."""
    log_file = _get_log_file(date)
    if log_file.exists():
        with log_file.open(encoding="utf-8") as f:
            data: list[dict[str, Any]] = json.load(f)
            return data
    return []


def _save_log(date: str, logs: list[dict[str, Any]]) -> None:
    """Save logs for a specific date."""
    log_file = _get_log_file(date)
    with log_file.open("w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def add_daily_log(
    db: Database,  # noqa: ARG001 - kept for interface compatibility
    content: str,
    date: str | None = None,
) -> str:
    """
    Add a daily log entry.

    Args:
        db: Database instance (not used, kept for interface compatibility)
        content: Log content
        date: Date in YYYY-MM-DD format, defaults to today

    Returns:
        Confirmation message
    """
    log_date = date or datetime.now().strftime("%Y-%m-%d")
    logger.info("Adding daily log for %s", log_date)

    logs = _load_log(log_date)
    logs.append(
        {
            "content": content,
            "time": datetime.now().strftime("%H:%M:%S"),
            "created_at": datetime.now().isoformat(),
        }
    )
    _save_log(log_date, logs)

    logger.debug("Log saved to %s", _get_log_file(log_date))
    return f"Logged entry for {log_date}"


def search_daily_log(
    db: Database,  # noqa: ARG001 - kept for interface compatibility
    keyword: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """
    Search daily logs.

    Args:
        db: Database instance (not used, kept for interface compatibility)
        keyword: Keyword to search
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Search results
    """
    log_dir = _get_log_dir()

    # Determine date range
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    logger.info("Searching logs from %s to %s (keyword=%s)", start_date, end_date, keyword)

    # Find matching log files
    results: list[tuple[str, dict[str, Any]]] = []
    for log_file in sorted(log_dir.glob("*.json"), reverse=True):
        file_date = log_file.stem  # YYYY-MM-DD
        if start_date <= file_date <= end_date:
            logs = _load_log(file_date)
            for log in logs:
                if keyword is None or keyword.lower() in log["content"].lower():
                    results.append((file_date, log))

    if not results:
        return "No matching log entries found"

    output_lines = ["Daily Logs:", ""]

    current_date: str | None = None
    for file_date, log in results:
        if file_date != current_date:
            if current_date is not None:
                output_lines.append("")
            output_lines.append(f"Date: {file_date}")
            current_date = file_date

        time_str = log.get("time", "")
        content = log["content"]
        # Truncate long content
        display_content = content if len(content) <= 100 else content[:100] + "..."

        if time_str:
            output_lines.append(f"  [{time_str}] {display_content}")
        else:
            output_lines.append(f"  - {display_content}")

    logger.info("Found %d matching log entries", len(results))
    return "\n".join(output_lines)
