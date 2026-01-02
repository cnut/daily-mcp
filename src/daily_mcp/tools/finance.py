"""Finance tools for recording income and expenses."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from daily_mcp.logging import get_logger

if TYPE_CHECKING:
    from daily_mcp.db import Database

logger = get_logger("tools.finance")


def record_expense(
    db: Database,
    amount: float,
    category: str,
    note: str | None = None,
    datetime_str: str | None = None,
) -> str:
    """
    Record an expense.

    Args:
        db: Database instance
        amount: Expense amount
        category: Expense category
        note: Optional note
        datetime_str: Datetime in YYYY-MM-DD HH:MM:SS format, defaults to now

    Returns:
        Confirmation message
    """
    expense_datetime = datetime_str or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("Recording expense: %.2f in %s", amount, category)

    db.execute(
        """
        INSERT INTO finance (type, amount, category, note, datetime)
        VALUES ('expense', ?, ?, ?, ?)
        """,
        (amount, category, note, expense_datetime),
    )
    db.commit()

    result = f"Recorded expense: {amount}, category: {category}"
    if note:
        result += f", note: {note}"
    return result


def record_income(
    db: Database,
    amount: float,
    source: str,
    note: str | None = None,
    datetime_str: str | None = None,
) -> str:
    """
    Record an income.

    Args:
        db: Database instance
        amount: Income amount
        source: Income source
        note: Optional note
        datetime_str: Datetime in YYYY-MM-DD HH:MM:SS format, defaults to now

    Returns:
        Confirmation message
    """
    income_datetime = datetime_str or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("Recording income: %.2f from %s", amount, source)

    db.execute(
        """
        INSERT INTO finance (type, amount, source, note, datetime)
        VALUES ('income', ?, ?, ?, ?)
        """,
        (amount, source, note, income_datetime),
    )
    db.commit()

    result = f"Recorded income: {amount}, source: {source}"
    if note:
        result += f", note: {note}"
    return result


def query_finance(db: Database, sql: str) -> str:
    """
    Query finance records with SQL.

    Args:
        db: Database instance
        sql: SQL query (only SELECT allowed)

    Returns:
        Query results formatted as table
    """
    logger.info("Querying finance with SQL")
    logger.debug("SQL: %s", sql)

    # Basic SQL injection prevention - only allow SELECT
    sql_lower = sql.strip().lower()
    if not sql_lower.startswith("select"):
        logger.warning("Non-SELECT query attempted: %s", sql[:50])
        return "Error: Only SELECT queries are allowed"

    # Ensure query is on finance table
    if "finance" not in sql_lower:
        return "Error: Please query the finance table"

    try:
        cursor = db.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        if not rows:
            return "No results found"

        # Format as table
        output = " | ".join(columns) + "\n"
        output += "-" * len(output) + "\n"
        for row in rows:
            output += " | ".join(str(v) for v in row) + "\n"

        logger.info("Query returned %d rows", len(rows))
        return output

    except Exception as e:
        logger.exception("Query error: %s", e)
        return f"Query error: {e!s}"
