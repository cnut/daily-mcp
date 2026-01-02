"""Todo tools for task management."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from daily_mcp.logging import get_logger

if TYPE_CHECKING:
    from daily_mcp.db import Database

logger = get_logger("tools.todo")


def add_todo(
    db: Database,
    content: str,
    topic: str | None = None,
    due_datetime: str | None = None,
) -> str:
    """
    Add a todo item.

    Args:
        db: Database instance
        content: Todo content
        topic: Optional topic/project
        due_datetime: Optional due datetime in YYYY-MM-DD HH:MM:SS format

    Returns:
        Confirmation message
    """
    logger.info("Adding todo: %s", content[:50])

    db.execute(
        """
        INSERT INTO todo (content, topic, due_datetime)
        VALUES (?, ?, ?)
        """,
        (content, topic, due_datetime),
    )
    db.commit()

    result = f"Added todo: {content}"
    if topic:
        result += f", topic: {topic}"
    if due_datetime:
        result += f", due: {due_datetime}"
    return result


def complete_todo(
    db: Database,
    todo_id: int | None = None,
    content_match: str | None = None,
) -> str:
    """
    Mark a todo as completed.

    Args:
        db: Database instance
        todo_id: Todo ID to complete
        content_match: Or match by content keyword

    Returns:
        Confirmation message or error
    """
    if todo_id:
        logger.info("Completing todo by ID: %d", todo_id)
        result = db.fetchone(
            "SELECT id, content FROM todo WHERE id = ? AND status = 'pending'",
            (todo_id,),
        )
        if not result:
            return f"Error: Todo with ID {todo_id} not found"

        db.execute(
            "UPDATE todo SET status = 'completed', completed_at = ? WHERE id = ?",
            (datetime.now().isoformat(), todo_id),
        )
        db.commit()
        return f"Completed todo: {result[1]}"

    if content_match:
        logger.info("Completing todo by content match: %s", content_match)
        result = db.fetchone(
            "SELECT id, content FROM todo WHERE content LIKE ? AND status = 'pending' LIMIT 1",
            (f"%{content_match}%",),
        )
        if not result:
            return f"Error: No pending todo found matching '{content_match}'"

        db.execute(
            "UPDATE todo SET status = 'completed', completed_at = ? WHERE id = ?",
            (datetime.now().isoformat(), result[0]),
        )
        db.commit()
        return f"Completed todo: {result[1]}"

    return "Error: Please provide todo_id or content_match"


def list_todos(
    db: Database,
    topic: str | None = None,
    status: str = "pending",
    include_overdue_reminder: bool = True,
) -> str:
    """
    List todos with optional filters.

    Args:
        db: Database instance
        topic: Filter by topic
        status: Filter by status ('pending', 'completed', 'all')
        include_overdue_reminder: Include overdue warning

    Returns:
        Formatted todo list
    """
    logger.info("Listing todos (topic=%s, status=%s)", topic, status)

    conditions: list[str] = []
    params: list[str] = []

    if status != "all":
        conditions.append("status = ?")
        params.append(status)

    if topic:
        conditions.append("topic = ?")
        params.append(topic)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    rows = db.fetchall(
        f"""
        SELECT id, content, topic, status, due_datetime, created_at
        FROM todo
        WHERE {where_clause}
        ORDER BY
            CASE WHEN due_datetime IS NOT NULL THEN 0 ELSE 1 END,
            due_datetime ASC,
            created_at DESC
        """,
        tuple(params),
    )

    if not rows:
        return "No todos found"

    now = datetime.now()
    output_lines = ["Todo List:", ""]
    overdue_count = 0

    for row in rows:
        id_, content, topic_, status_, due_datetime_, _created_at = row
        line = f"  [{id_}] {content}"

        if topic_:
            line += f" [{topic_}]"

        if status_ == "completed":
            line = f"  [x] {line[4:]}"
        else:
            if due_datetime_:
                due = datetime.strptime(due_datetime_, "%Y-%m-%d %H:%M:%S")
                if due < now:
                    line += f" OVERDUE({due_datetime_})"
                    overdue_count += 1
                else:
                    line += f" (due: {due_datetime_})"
            line = f"  [ ] {line[4:]}"

        output_lines.append(line)

    # Add overdue reminder
    if include_overdue_reminder and overdue_count > 0:
        output_lines.insert(1, f"Warning: You have {overdue_count} overdue task(s)!")
        output_lines.insert(2, "")

    logger.info("Listed %d todos (%d overdue)", len(rows), overdue_count)
    return "\n".join(output_lines)
