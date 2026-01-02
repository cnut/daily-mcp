"""MCP Handlers - Tools, Resources, and Prompts registration."""

from __future__ import annotations

from datetime import datetime
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
    AddDailyLog,
    AddTodo,
    CompleteTodo,
    DailyTools,
    ListTodos,
    QueryFinance,
    QueryHealth,
    RecordExpense,
    RecordHealth,
    RecordIncome,
    SearchDailyLog,
)
from daily_mcp.tools import daily_log, finance, health, todo

if TYPE_CHECKING:
    from collections.abc import Callable

    from mcp.server import Server

    from daily_mcp.db import Database

logger = get_logger("handlers")


def register_tools(server: Server, db: Database) -> None:
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
                description="Add a todo item with optional topic and due date.",
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
                name=DailyTools.ADD_DAILY_LOG,
                description="Add a free-form daily log entry.",
                inputSchema=AddDailyLog.model_json_schema(),
            ),
            Tool(
                name=DailyTools.SEARCH_DAILY_LOG,
                description="Search daily logs by keyword or date range.",
                inputSchema=SearchDailyLog.model_json_schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls."""
        logger.info("Tool called: %s", name)
        logger.debug("Arguments: %s", arguments)

        try:
            result = _dispatch_tool(db, name, arguments)
            logger.debug("Tool result: %s", result[:200] if len(result) > 200 else result)
            return [TextContent(type="text", text=result)]
        except Exception as e:
            logger.exception("Error calling tool %s: %s", name, e)
            return [TextContent(type="text", text=f"Error: {e!s}")]


def _dispatch_tool(db: Database, name: str, arguments: dict[str, Any]) -> str:
    """Dispatch tool call to appropriate handler."""
    handlers: dict[str, Callable[[Database, dict[str, Any]], str]] = {
        DailyTools.RECORD_EXPENSE: lambda d, a: finance.record_expense(d, **a),
        DailyTools.RECORD_INCOME: lambda d, a: finance.record_income(d, **a),
        DailyTools.QUERY_FINANCE: lambda d, a: finance.query_finance(d, a.get("sql", "")),
        DailyTools.ADD_TODO: lambda d, a: todo.add_todo(d, **a),
        DailyTools.COMPLETE_TODO: lambda d, a: todo.complete_todo(d, **a),
        DailyTools.LIST_TODOS: lambda d, a: todo.list_todos(d, **a),
        DailyTools.RECORD_HEALTH: lambda d, a: health.record_health(d, **a),
        DailyTools.QUERY_HEALTH: lambda d, a: health.query_health(d, **a),
        DailyTools.ADD_DAILY_LOG: lambda d, a: daily_log.add_daily_log(d, **a),
        DailyTools.SEARCH_DAILY_LOG: lambda d, a: daily_log.search_daily_log(d, **a),
    }

    handler = handlers.get(name)
    if handler:
        return handler(db, arguments)

    logger.warning("Unknown tool: %s", name)
    return f"Unknown tool: {name}"


def register_resources(server: Server, db: Database) -> None:
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
        return _resolve_resource(db, str(uri))


def _resolve_resource(db: Database, uri_str: str) -> str:
    """Resolve resource URI to content."""
    if uri_str == "daily://summary/today":
        return get_daily_summary(db)
    if uri_str == "daily://summary/weekly":
        return get_weekly_summary(db)

    # Support date-specific summaries: daily://summary/2024-01-15
    if uri_str.startswith("daily://summary/"):
        date_part = uri_str.replace("daily://summary/", "")
        try:
            datetime.strptime(date_part, "%Y-%m-%d")
            return get_daily_summary(db, date_part)
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
