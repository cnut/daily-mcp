"""Daily MCP Server - Main entry point."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from daily_mcp.db import Database
from daily_mcp.logging import get_logger, setup_logging
from daily_mcp.tools import daily_log, finance, health, todo

# Setup logging
log_level = os.environ.get("DAILY_MCP_LOG_LEVEL", "INFO")
log_file = os.environ.get("DAILY_MCP_LOG_FILE")
setup_logging(
    level=getattr(__import__("logging"), log_level.upper(), 20),
    log_file=Path(log_file) if log_file else None,
)
logger = get_logger("server")

# Create server instance
server = Server("daily-mcp")
db = Database()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    logger.debug("Listing tools")
    return [
        # Finance tools
        Tool(
            name="record_expense",
            description="Record an expense with amount, category and optional note.",
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Amount"},
                    "category": {
                        "type": "string",
                        "description": "Category (e.g., food, transport, shopping)",
                    },
                    "note": {"type": "string", "description": "Optional note"},
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format, defaults to today",
                    },
                },
                "required": ["amount", "category"],
            },
        ),
        Tool(
            name="record_income",
            description="Record an income with amount, source and optional note.",
            inputSchema={
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Amount"},
                    "source": {
                        "type": "string",
                        "description": "Source (e.g., salary, bonus, investment)",
                    },
                    "note": {"type": "string", "description": "Optional note"},
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format, defaults to today",
                    },
                },
                "required": ["amount", "source"],
            },
        ),
        Tool(
            name="query_finance",
            description="Query finance records with SQL. Table name is 'finance'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL query statement, table name is 'finance'",
                    },
                },
                "required": ["sql"],
            },
        ),
        # Todo tools
        Tool(
            name="add_todo",
            description="Add a todo item with optional topic and due date.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Todo content"},
                    "topic": {
                        "type": "string",
                        "description": "Topic/Project (e.g., work, life, fitness)",
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in YYYY-MM-DD format",
                    },
                },
                "required": ["content"],
            },
        ),
        Tool(
            name="complete_todo",
            description="Mark a todo as completed by ID or content match.",
            inputSchema={
                "type": "object",
                "properties": {
                    "todo_id": {"type": "integer", "description": "Todo ID"},
                    "content_match": {
                        "type": "string",
                        "description": "Or match by content keyword",
                    },
                },
            },
        ),
        Tool(
            name="list_todos",
            description="List todos, optionally filter by topic and status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Filter by topic"},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed", "all"],
                        "description": "Filter by status, defaults to 'pending'",
                    },
                    "include_overdue_reminder": {
                        "type": "boolean",
                        "description": "Include overdue reminder, defaults to true",
                    },
                },
            },
        ),
        # Health tools
        Tool(
            name="record_health",
            description="Record health metrics like blood pressure, heart rate, weight, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "metric_type": {
                        "type": "string",
                        "enum": [
                            "blood_pressure",
                            "heart_rate",
                            "weight",
                            "blood_sugar",
                            "sleep",
                            "exercise",
                        ],
                        "description": "Metric type",
                    },
                    "value": {
                        "type": "string",
                        "description": "Value (e.g., '120/80' for blood pressure)",
                    },
                    "unit": {"type": "string", "description": "Unit (optional, has defaults)"},
                    "note": {"type": "string", "description": "Optional note"},
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format, defaults to today",
                    },
                },
                "required": ["metric_type", "value"],
            },
        ),
        Tool(
            name="query_health",
            description="Query health records by metric type, time range, or SQL.",
            inputSchema={
                "type": "object",
                "properties": {
                    "metric_type": {"type": "string", "description": "Filter by metric type"},
                    "days": {"type": "integer", "description": "Last N days, defaults to 30"},
                    "sql": {
                        "type": "string",
                        "description": "Or use SQL query directly, table name is 'health'",
                    },
                },
            },
        ),
        # Daily log tools
        Tool(
            name="add_daily_log",
            description="Add a free-form daily log entry.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Log content"},
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format, defaults to today",
                    },
                },
                "required": ["content"],
            },
        ),
        Tool(
            name="search_daily_log",
            description="Search daily logs by keyword or date range.",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "Keyword to search"},
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format",
                    },
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    logger.info("Tool called: %s", name)
    logger.debug("Arguments: %s", arguments)

    try:
        result: str
        if name == "record_expense":
            result = finance.record_expense(db, **arguments)
        elif name == "record_income":
            result = finance.record_income(db, **arguments)
        elif name == "query_finance":
            result = finance.query_finance(db, arguments.get("sql", ""))
        elif name == "add_todo":
            result = todo.add_todo(db, **arguments)
        elif name == "complete_todo":
            result = todo.complete_todo(db, **arguments)
        elif name == "list_todos":
            result = todo.list_todos(db, **arguments)
        elif name == "record_health":
            result = health.record_health(db, **arguments)
        elif name == "query_health":
            result = health.query_health(db, **arguments)
        elif name == "add_daily_log":
            result = daily_log.add_daily_log(db, **arguments)
        elif name == "search_daily_log":
            result = daily_log.search_daily_log(db, **arguments)
        else:
            logger.warning("Unknown tool: %s", name)
            result = f"Unknown tool: {name}"

        logger.debug("Tool result: %s", result[:200] if len(result) > 200 else result)
        return [TextContent(type="text", text=result)]

    except Exception as e:
        logger.exception("Error calling tool %s: %s", name, e)
        return [TextContent(type="text", text=f"Error: {e!s}")]


async def run() -> None:
    """Run the MCP server."""
    logger.info("Starting daily-mcp server")
    db.init()
    logger.info("Database initialized at %s", db.db_path)

    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server running on stdio")
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    """Main entry point."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
