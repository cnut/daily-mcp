"""MCP Handlers - Tools, Resources, and Prompts registration."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path  # noqa: TC003 - used at runtime for function signatures
from typing import TYPE_CHECKING, Any

from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    Resource,
    TextContent,
    Tool,
)
from pydantic import AnyUrl

from daily_mcp.logging import get_logger
from daily_mcp.prompts import PROMPTS
from daily_mcp.resources import get_daily_summary, get_weekly_summary
from daily_mcp.schemas import (
    AddDiary,
    AddTodo,
    CompleteTodo,
    DailyTools,
    ListTodos,
    QueryFinance,
    QueryHealth,
    RecordExpense,
    RecordHealth,
    RecordIncome,
    SearchDiary,
)
from daily_mcp.tools import diary, finance, health, todo

if TYPE_CHECKING:
    from collections.abc import Callable

    from mcp.server import Server

    from daily_mcp.db import Database

logger = get_logger("handlers")


def register_tools(server: Server, db: Database, diary_path: Path) -> None:
    """Register all tool handlers."""

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        logger.debug("Listing tools")
        return [
            Tool(
                name=DailyTools.RECORD_EXPENSE,
                description="Record an expense with amount, category and optional note.",
                inputSchema=RecordExpense.model_json_schema(),
            ),
            Tool(
                name=DailyTools.RECORD_INCOME,
                description="Record an income with amount, source and optional note.",
                inputSchema=RecordIncome.model_json_schema(),
            ),
            Tool(
                name=DailyTools.QUERY_FINANCE,
                description="Query finance records with SQL. Table name is 'finance'.",
                inputSchema=QueryFinance.model_json_schema(),
            ),
            Tool(
                name=DailyTools.ADD_TODO,
                description="Add a todo item with optional topic and due datetime.",
                inputSchema=AddTodo.model_json_schema(),
            ),
            Tool(
                name=DailyTools.COMPLETE_TODO,
                description="Mark a todo as completed by ID or content match.",
                inputSchema=CompleteTodo.model_json_schema(),
            ),
            Tool(
                name=DailyTools.LIST_TODOS,
                description="List todos, optionally filter by topic and status.",
                inputSchema=ListTodos.model_json_schema(),
            ),
            Tool(
                name=DailyTools.RECORD_HEALTH,
                description="Record health metrics like blood pressure, heart rate, weight.",
                inputSchema=RecordHealth.model_json_schema(),
            ),
            Tool(
                name=DailyTools.QUERY_HEALTH,
                description="Query health records by metric type, time range, or SQL.",
                inputSchema=QueryHealth.model_json_schema(),
            ),
            Tool(
                name=DailyTools.ADD_DIARY,
                description="Add a free-form diary entry with optional tags.",
                inputSchema=AddDiary.model_json_schema(),
            ),
            Tool(
                name=DailyTools.SEARCH_DIARY,
                description="Search diary entries by keyword, tag, or datetime range.",
                inputSchema=SearchDiary.model_json_schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls."""
        logger.info("Tool called: %s", name)
        logger.debug("Arguments: %s", arguments)

        try:
            result = _dispatch_tool(db, diary_path, name, arguments)
            logger.debug("Tool result: %s", result[:200] if len(result) > 200 else result)
            return [TextContent(type="text", text=result)]
        except Exception as e:
            logger.exception("Error calling tool %s: %s", name, e)
            return [TextContent(type="text", text=f"Error: {e!s}")]


def _dispatch_tool(db: Database, diary_path: Path, name: str, arguments: dict[str, Any]) -> str:
    """Dispatch tool call to appropriate handler."""
    handlers: dict[str, Callable[[], str]] = {
        DailyTools.RECORD_EXPENSE: lambda: finance.record_expense(
            db,
            amount=arguments["amount"],
            category=arguments["category"],
            note=arguments.get("note"),
            datetime_str=arguments.get("datetime"),
        ),
        DailyTools.RECORD_INCOME: lambda: finance.record_income(
            db,
            amount=arguments["amount"],
            source=arguments["source"],
            note=arguments.get("note"),
            datetime_str=arguments.get("datetime"),
        ),
        DailyTools.QUERY_FINANCE: lambda: finance.query_finance(db, arguments.get("sql", "")),
        DailyTools.ADD_TODO: lambda: todo.add_todo(
            db,
            content=arguments["content"],
            topic=arguments.get("topic"),
            due_datetime=arguments.get("due_datetime"),
        ),
        DailyTools.COMPLETE_TODO: lambda: todo.complete_todo(db, **arguments),
        DailyTools.LIST_TODOS: lambda: todo.list_todos(db, **arguments),
        DailyTools.RECORD_HEALTH: lambda: health.record_health(
            db,
            metric_type=arguments["metric_type"],
            value=arguments["value"],
            unit=arguments.get("unit"),
            note=arguments.get("note"),
            datetime_str=arguments.get("datetime"),
        ),
        DailyTools.QUERY_HEALTH: lambda: health.query_health(db, **arguments),
        DailyTools.ADD_DIARY: lambda: diary.add_diary(
            diary_path,
            content=arguments["content"],
            tags=arguments.get("tags"),
            datetime_str=arguments.get("datetime"),
        ),
        DailyTools.SEARCH_DIARY: lambda: diary.search_diary(
            diary_path,
            keyword=arguments.get("keyword"),
            tag=arguments.get("tag"),
            start_datetime=arguments.get("start_datetime"),
            end_datetime=arguments.get("end_datetime"),
        ),
    }

    handler = handlers.get(name)
    if handler:
        return handler()

    logger.warning("Unknown tool: %s", name)
    return f"Unknown tool: {name}"


def register_resources(server: Server, db: Database, diary_path: Path) -> None:
    """Register all resource handlers."""

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """List available resources."""
        logger.debug("Listing resources")
        return [
            Resource(
                uri=AnyUrl("daily://summary/today"),
                name="Today's Summary",
                description="A summary of today's activities, finances, todos, and health",
                mimeType="text/plain",
            ),
            Resource(
                uri=AnyUrl("daily://summary/weekly"),
                name="Weekly Summary",
                description="A summary of the last 7 days",
                mimeType="text/plain",
            ),
        ]

    @server.read_resource()
    async def read_resource(uri: AnyUrl) -> str:
        """Read a resource by URI."""
        logger.debug("Reading resource: %s", uri)
        return _resolve_resource(db, diary_path, str(uri))


def _resolve_resource(db: Database, diary_path: Path, uri_str: str) -> str:
    """Resolve resource URI to content."""
    if uri_str == "daily://summary/today":
        return get_daily_summary(db, diary_path)
    if uri_str == "daily://summary/weekly":
        return get_weekly_summary(db, diary_path)

    # Support date-specific summaries: daily://summary/2024-01-15
    if uri_str.startswith("daily://summary/"):
        date_part = uri_str.replace("daily://summary/", "")
        try:
            datetime.strptime(date_part, "%Y-%m-%d")
            return get_daily_summary(db, diary_path, date_part)
        except ValueError:
            pass

    raise ValueError(f"Unknown resource: {uri_str}")


def register_prompts(server: Server) -> None:
    """Register all prompt handlers."""

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """List available prompts."""
        logger.debug("Listing prompts")
        return [
            Prompt(
                name=prompt_data["name"],
                description=prompt_data["description"],
                arguments=[
                    PromptArgument(
                        name=arg["name"],
                        description=arg["description"],
                        required=arg.get("required", False),
                    )
                    for arg in prompt_data["arguments"]
                ],
            )
            for prompt_data in PROMPTS.values()
        ]

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
        """Get a specific prompt with arguments."""
        logger.debug("Getting prompt: %s with args: %s", name, arguments)

        if name not in PROMPTS:
            raise ValueError(f"Unknown prompt: {name}")

        prompt_data = PROMPTS[name]
        args = _apply_prompt_defaults(name, arguments or {})

        try:
            formatted = prompt_data["template"].format(**args)
        except KeyError as e:
            raise ValueError(f"Missing required argument: {e}") from e

        return GetPromptResult(
            description=prompt_data["description"],
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=formatted.strip()),
                )
            ],
        )


def _apply_prompt_defaults(name: str, args: dict[str, str]) -> dict[str, str]:
    """Apply default values for prompt arguments."""
    result = dict(args)

    if name == "daily-review":
        result.setdefault("date", datetime.now().strftime("%Y-%m-%d"))
    elif name == "weekly-planning":
        result.setdefault("focus", "general productivity")
    elif name == "health-checkup":
        result.setdefault("metric_type", "all")
        result.setdefault("days", "30")

    return result
