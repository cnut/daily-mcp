"""Pydantic schemas for tool parameters."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

# =============================================================================
# Tool Names Enum
# =============================================================================


class DailyTools(str, Enum):
    """All available tool names."""

    # Finance
    RECORD_EXPENSE = "record_expense"
    RECORD_INCOME = "record_income"
    QUERY_FINANCE = "query_finance"

    # Todo
    ADD_TODO = "add_todo"
    COMPLETE_TODO = "complete_todo"
    LIST_TODOS = "list_todos"

    # Health
    RECORD_HEALTH = "record_health"
    QUERY_HEALTH = "query_health"

    # Daily Log
    ADD_DAILY_LOG = "add_daily_log"
    SEARCH_DAILY_LOG = "search_daily_log"


# =============================================================================
# Finance Schemas
# =============================================================================


class RecordExpense(BaseModel):
    """Schema for recording an expense."""

    amount: float = Field(..., description="Expense amount", gt=0)
    category: str = Field(
        ...,
        description="Expense category (e.g., food, transport, shopping, entertainment)",
    )
    note: str | None = Field(None, description="Optional note for this expense")
    date: str | None = Field(
        None,
        description="Date in YYYY-MM-DD format, defaults to today",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )


class RecordIncome(BaseModel):
    """Schema for recording an income."""

    amount: float = Field(..., description="Income amount", gt=0)
    source: str = Field(
        ...,
        description="Income source (e.g., salary, bonus, investment, freelance)",
    )
    note: str | None = Field(None, description="Optional note for this income")
    date: str | None = Field(
        None,
        description="Date in YYYY-MM-DD format, defaults to today",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )


class QueryFinance(BaseModel):
    """Schema for querying finance records."""

    sql: str = Field(
        ...,
        description=(
            "SQL SELECT query on the 'finance' table. "
            "Columns: id, type, amount, category, source, note, date, created_at"
        ),
    )


# =============================================================================
# Todo Schemas
# =============================================================================


class AddTodo(BaseModel):
    """Schema for adding a todo item."""

    content: str = Field(..., description="Todo item content")
    topic: str | None = Field(
        None,
        description="Topic/Project category (e.g., work, personal, fitness, learning)",
    )
    due_date: str | None = Field(
        None,
        description="Due date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )


class CompleteTodo(BaseModel):
    """Schema for completing a todo item."""

    todo_id: int | None = Field(None, description="Todo ID to mark as completed")
    content_match: str | None = Field(
        None,
        description="Keyword to match todo content (used if todo_id not provided)",
    )


class ListTodos(BaseModel):
    """Schema for listing todos."""

    topic: str | None = Field(None, description="Filter by topic/project")
    status: Literal["pending", "completed", "all"] = Field(
        "pending",
        description="Filter by status: 'pending', 'completed', or 'all'",
    )
    include_overdue_reminder: bool = Field(
        True,
        description="Include warning for overdue tasks",
    )


# =============================================================================
# Health Schemas
# =============================================================================


class RecordHealth(BaseModel):
    """Schema for recording a health metric."""

    metric_type: Literal[
        "blood_pressure",
        "heart_rate",
        "weight",
        "blood_sugar",
        "sleep",
        "exercise",
    ] = Field(..., description="Type of health metric to record")
    value: str = Field(
        ...,
        description=(
            "Metric value. Examples: '120/80' for blood pressure, "
            "'72' for heart rate, '70.5' for weight"
        ),
    )
    unit: str | None = Field(
        None,
        description="Unit (optional, defaults based on metric type)",
    )
    note: str | None = Field(None, description="Optional note")
    date: str | None = Field(
        None,
        description="Date in YYYY-MM-DD format, defaults to today",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )


class QueryHealth(BaseModel):
    """Schema for querying health records."""

    metric_type: (
        Literal["blood_pressure", "heart_rate", "weight", "blood_sugar", "sleep", "exercise"] | None
    ) = Field(None, description="Filter by metric type")
    days: int = Field(30, description="Query last N days of records", ge=1, le=365)
    sql: str | None = Field(
        None,
        description=(
            "Direct SQL query (overrides other filters). "
            "Table: 'health', Columns: id, metric_type, value, unit, note, date"
        ),
    )


# =============================================================================
# Daily Log Schemas
# =============================================================================


class AddDailyLog(BaseModel):
    """Schema for adding a daily log entry."""

    content: str = Field(..., description="Free-form log content")
    date: str | None = Field(
        None,
        description="Date in YYYY-MM-DD format, defaults to today",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )


class SearchDailyLog(BaseModel):
    """Schema for searching daily logs."""

    keyword: str | None = Field(None, description="Keyword to search in log content")
    start_date: str | None = Field(
        None,
        description="Start date in YYYY-MM-DD format (defaults to 30 days ago)",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    end_date: str | None = Field(
        None,
        description="End date in YYYY-MM-DD format (defaults to today)",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
