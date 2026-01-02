"""MCP Resources - Dynamic data exposed to the Agent."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path  # noqa: TC003 - used at runtime for function signatures
from typing import TYPE_CHECKING, Any

from daily_mcp.logging import get_logger
from daily_mcp.tools import diary

if TYPE_CHECKING:
    from daily_mcp.db import Database

logger = get_logger("resources")


def _format_finance_section(finance_rows: list[Any]) -> list[str]:
    """Format finance data into summary lines."""
    if not finance_rows:
        return ["💰 Finance: No transactions", ""]

    lines = ["💰 Finance:"]
    total_income = 0.0
    total_expense = 0.0

    for row in finance_rows:
        type_, total, count = row
        if type_ == "income":
            total_income = float(total)
            lines.append(f"  Income: +{total:.2f} ({count} transactions)")
        else:
            total_expense = float(total)
            lines.append(f"  Expense: -{total:.2f} ({count} transactions)")

    net = total_income - total_expense
    lines.append(f"  Net: {net:+.2f}")
    lines.append("")
    return lines


def _format_todo_section(todo_rows: list[Any]) -> list[str]:
    """Format todo data into summary lines."""
    pending = 0
    completed = 0

    for row in todo_rows:
        status, count = row
        if status == "pending":
            pending = count
        else:
            completed = count

    return [
        "✅ Todos:",
        f"  Completed: {completed}",
        f"  Pending: {pending}",
        "",
    ]


def _format_health_section(health_rows: list[Any]) -> list[str]:
    """Format health data into summary lines."""
    if not health_rows:
        return ["❤️ Health: No records", ""]

    lines = ["❤️ Health Metrics:"]
    for row in health_rows:
        metric_type, value, unit = row
        lines.append(f"  {metric_type}: {value} {unit or ''}")
    lines.append("")
    return lines


def _format_diary_section(diary_path: Path, target_date: str) -> list[str]:
    """Format diary data into summary lines."""
    entries = diary._load_diary(diary_path, target_date)
    if not entries:
        return ["📝 Diary: No entries"]

    lines = [f"📝 Diary: {len(entries)} entries"]
    for entry in entries[:3]:  # Show first 3 entries
        content = entry["content"]
        preview = content[:50] + "..." if len(content) > 50 else content
        datetime_str = entry.get("datetime", entry.get("time", ""))
        # Show only time part if datetime contains date
        display_time = datetime_str.split(" ")[-1] if " " in datetime_str else datetime_str
        lines.append(f"  [{display_time}] {preview}")

    if len(entries) > 3:
        lines.append(f"  ... and {len(entries) - 3} more entries")

    return lines


def get_daily_summary(db: Database, diary_path: Path, date: str | None = None) -> str:
    """
    Generate a daily summary for a specific date.

    Args:
        db: Database instance
        diary_path: Directory containing diary files
        date: Date in YYYY-MM-DD format, defaults to today

    Returns:
        Formatted daily summary
    """
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    logger.info("Generating daily summary for %s", target_date)

    lines = [f"📅 Daily Summary for {target_date}", "=" * 40, ""]

    # Finance summary
    finance_rows = db.fetchall(
        """
        SELECT type, SUM(amount) as total, COUNT(*) as count
        FROM finance WHERE date(datetime) = ? GROUP BY type
        """,
        (target_date,),
    )
    lines.extend(_format_finance_section(finance_rows))

    # Todo summary
    todo_rows = db.fetchall(
        """
        SELECT status, COUNT(*) as count FROM todo
        WHERE date(created_at) = ? OR date(completed_at) = ? GROUP BY status
        """,
        (target_date, target_date),
    )
    lines.extend(_format_todo_section(todo_rows))

    # Health summary
    health_rows = db.fetchall(
        """
        SELECT metric_type, value, unit FROM health
        WHERE date(datetime) = ? ORDER BY metric_type
        """,
        (target_date,),
    )
    lines.extend(_format_health_section(health_rows))

    # Diary summary
    lines.extend(_format_diary_section(diary_path, target_date))

    return "\n".join(lines)


def get_weekly_summary(db: Database, diary_path: Path) -> str:
    """
    Generate a weekly summary (last 7 days).

    Args:
        db: Database instance
        diary_path: Directory containing diary files

    Returns:
        Formatted weekly summary
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    logger.info("Generating weekly summary from %s to %s", start_str, end_str)

    lines = [f"📊 Weekly Summary ({start_str} to {end_str})", "=" * 50, ""]

    # Finance summary
    lines.extend(_build_weekly_finance(db, start_str, end_str))

    # Todo summary
    lines.extend(_build_weekly_todos(db, start_str, end_str))

    # Health trends
    lines.extend(_build_weekly_health(db, start_str, end_str))

    # Diary count
    lines.extend(_build_weekly_diary(diary_path, start_str, end_str))

    return "\n".join(lines)


def _build_weekly_finance(db: Database, start_str: str, end_str: str) -> list[str]:
    """Build weekly finance section."""
    lines = ["💰 Finance Overview:"]
    total_income = 0.0
    total_expense = 0.0

    finance_rows = db.fetchall(
        """
        SELECT type, SUM(amount) as total, COUNT(*) as count
        FROM finance WHERE date(datetime) >= ? AND date(datetime) <= ? GROUP BY type
        """,
        (start_str, end_str),
    )

    for row in finance_rows:
        type_, total, count = row
        if type_ == "income":
            total_income = float(total)
            lines.append(f"  Total Income: +{total:.2f} ({count} transactions)")
        else:
            total_expense = float(total)
            lines.append(f"  Total Expense: -{total:.2f} ({count} transactions)")

    if finance_rows:
        net = total_income - total_expense
        lines.append(f"  Net: {net:+.2f}")

    # Top expense categories
    category_rows = db.fetchall(
        """
        SELECT category, SUM(amount) as total FROM finance
        WHERE type = 'expense' AND date(datetime) >= ? AND date(datetime) <= ?
        GROUP BY category ORDER BY total DESC LIMIT 5
        """,
        (start_str, end_str),
    )
    if category_rows:
        lines.append("  Top Categories:")
        for row in category_rows:
            category, total = row
            lines.append(f"    - {category}: {total:.2f}")
    lines.append("")
    return lines


def _build_weekly_todos(db: Database, start_str: str, end_str: str) -> list[str]:
    """Build weekly todos section."""
    completed_count = db.fetchone(
        """
        SELECT COUNT(*) FROM todo WHERE status = 'completed'
        AND date(completed_at) >= ? AND date(completed_at) <= ?
        """,
        (start_str, end_str),
    )
    pending_count = db.fetchone(
        "SELECT COUNT(*) FROM todo WHERE status = 'pending'",
        (),
    )

    return [
        "✅ Todos:",
        f"  Completed this week: {completed_count[0] if completed_count else 0}",
        f"  Currently pending: {pending_count[0] if pending_count else 0}",
        "",
    ]


def _build_weekly_health(db: Database, start_str: str, end_str: str) -> list[str]:
    """Build weekly health section."""
    health_rows = db.fetchall(
        """
        SELECT metric_type, COUNT(*) as count, MIN(value) as min_val, MAX(value) as max_val
        FROM health WHERE date(datetime) >= ? AND date(datetime) <= ? GROUP BY metric_type
        """,
        (start_str, end_str),
    )

    if not health_rows:
        return []

    lines = ["❤️ Health Tracking:"]
    for row in health_rows:
        metric_type, count, min_val, max_val = row
        lines.append(f"  {metric_type}: {count} records (range: {min_val} - {max_val})")
    lines.append("")
    return lines


def _build_weekly_diary(diary_path: Path, start_str: str, end_str: str) -> list[str]:
    """Build weekly diary section."""
    entry_count = 0
    for diary_file in diary_path.glob("*.json"):
        file_date = diary_file.stem
        if start_str <= file_date <= end_str:
            entries = diary._load_diary(diary_path, file_date)
            entry_count += len(entries)

    return [f"📝 Diary: {entry_count} entries this week"]
