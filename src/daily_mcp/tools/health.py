"""Health tools for recording health metrics."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from daily_mcp.logging import get_logger

if TYPE_CHECKING:
    from daily_mcp.db import Database

logger = get_logger("tools.health")

METRIC_UNITS: dict[str, str] = {
    "blood_pressure": "mmHg",
    "heart_rate": "bpm",
    "weight": "kg",
    "blood_sugar": "mmol/L",
    "sleep": "hours",
    "exercise": "minutes",
}

METRIC_NAMES: dict[str, str] = {
    "blood_pressure": "Blood Pressure",
    "heart_rate": "Heart Rate",
    "weight": "Weight",
    "blood_sugar": "Blood Sugar",
    "sleep": "Sleep",
    "exercise": "Exercise",
}


def record_health(
    db: Database,
    metric_type: str,
    value: str,
    unit: str | None = None,
    note: str | None = None,
    date: str | None = None,
) -> str:
    """
    Record a health metric.

    Args:
        db: Database instance
        metric_type: Type of metric (blood_pressure, heart_rate, etc.)
        value: Metric value
        unit: Optional unit (has defaults per metric type)
        note: Optional note
        date: Date in YYYY-MM-DD format, defaults to today

    Returns:
        Confirmation message
    """
    record_date = date or datetime.now().strftime("%Y-%m-%d")
    unit = unit or METRIC_UNITS.get(metric_type, "")

    logger.info("Recording health metric: %s = %s", metric_type, value)

    db.execute(
        """
        INSERT INTO health (metric_type, value, unit, note, date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (metric_type, value, unit, note, record_date),
    )
    db.commit()

    name = METRIC_NAMES.get(metric_type, metric_type)
    result = f"Recorded {name}: {value} {unit}"
    if note:
        result += f", note: {note}"
    return result


def _query_health_sql(db: Database, sql: str) -> str:
    """Execute direct SQL query on health table."""
    logger.info("Querying health with SQL")
    logger.debug("SQL: %s", sql)

    sql_lower = sql.strip().lower()
    if not sql_lower.startswith("select"):
        return "Error: Only SELECT queries are allowed"
    if "health" not in sql_lower:
        return "Error: Please query the health table"

    try:
        cursor = db.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        if not rows:
            return "No results found"

        output = " | ".join(columns) + "\n"
        output += "-" * len(output) + "\n"
        for row in rows:
            output += " | ".join(str(v) for v in row) + "\n"

        return output

    except Exception as e:
        logger.exception("Query error: %s", e)
        return f"Query error: {e!s}"


def _format_health_rows(
    rows: list[Any],
    metric_type: str | None,
    days: int,
) -> str:
    """Format health query results."""
    if not rows:
        return f"No health records in the last {days} days"

    output_lines = [f"Health Records (last {days} days):", ""]

    if metric_type:
        name = METRIC_NAMES.get(metric_type, metric_type)
        output_lines[0] = f"{name} Records (last {days} days):"
        for row in rows:
            date_, value, unit, note = row
            line = f"  {date_}: {value} {unit or ''}"
            if note:
                line += f" ({note})"
            output_lines.append(line)
    else:
        for row in rows:
            date_, type_, value, unit, note = row
            name = METRIC_NAMES.get(type_, type_)
            line = f"  {date_} [{name}]: {value} {unit or ''}"
            if note:
                line += f" ({note})"
            output_lines.append(line)

    logger.info("Query returned %d records", len(rows))
    return "\n".join(output_lines)


def query_health(
    db: Database,
    metric_type: str | None = None,
    days: int = 30,
    sql: str | None = None,
) -> str:
    """
    Query health records.

    Args:
        db: Database instance
        metric_type: Filter by metric type
        days: Last N days to query (default 30)
        sql: Direct SQL query (overrides other filters)

    Returns:
        Query results
    """
    if sql:
        return _query_health_sql(db, sql)

    # Standard query
    logger.info("Querying health records (metric=%s, days=%d)", metric_type, days)
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    if metric_type:
        rows = db.fetchall(
            """
            SELECT date, value, unit, note
            FROM health
            WHERE metric_type = ? AND date >= ?
            ORDER BY date DESC
            """,
            (metric_type, start_date),
        )
    else:
        rows = db.fetchall(
            """
            SELECT date, metric_type, value, unit, note
            FROM health
            WHERE date >= ?
            ORDER BY date DESC, metric_type
            """,
            (start_date,),
        )

    return _format_health_rows(rows, metric_type, days)
