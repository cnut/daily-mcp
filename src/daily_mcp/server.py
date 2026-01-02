"""Daily MCP Server - Main entry point."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import click
from mcp.server import Server
from mcp.server.stdio import stdio_server

from daily_mcp.db import Database
from daily_mcp.handlers import register_prompts, register_resources, register_tools
from daily_mcp.logging import get_logger, setup_logging


async def serve(db_path: Path | None = None, diary_path: Path | None = None) -> None:
    """Run the MCP server."""
    logger = get_logger("server")
    logger.info("Starting daily-mcp server")

    # Initialize database
    db = Database(db_path)
    db.init()
    logger.info("Database initialized at %s", db.db_path)

    # Resolve diary path
    if diary_path is None:
        diary_path = Path.home() / ".daily-mcp" / "diary"
    diary_path.mkdir(parents=True, exist_ok=True)
    logger.info("Diary directory at %s", diary_path)

    # Create server instance
    server = Server("daily-mcp")

    # Register handlers
    register_tools(server, db, diary_path)
    register_resources(server, db, diary_path)
    register_prompts(server)

    # Run server
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server running on stdio")
        await server.run(read_stream, write_stream, server.create_initialization_options())


@click.command()
@click.option(
    "--db-path",
    "-d",
    type=click.Path(path_type=Path),
    default=None,
    help="Database file path (default: ~/.daily-mcp/data.db)",
)
@click.option(
    "--diary-path",
    type=click.Path(path_type=Path),
    default=None,
    help="Diary directory path (default: ~/.daily-mcp/diary)",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (-v for INFO, -vv for DEBUG)",
)
@click.option(
    "--log-file",
    type=click.Path(path_type=Path),
    default=None,
    help="Log file path (default: stderr only)",
)
@click.version_option(version="0.1.0", prog_name="daily-mcp")
def main(
    db_path: Path | None,
    diary_path: Path | None,
    verbose: int,
    log_file: Path | None,
) -> None:
    """Daily MCP Server - Personal daily life recording via MCP.

    A Model Context Protocol server for tracking finances, todos,
    health metrics, and daily logs.
    """
    # Configure logging level
    log_level = logging.WARNING
    if verbose == 1:
        log_level = logging.INFO
    elif verbose >= 2:
        log_level = logging.DEBUG

    setup_logging(level=log_level, log_file=log_file)

    # Run the server
    asyncio.run(serve(db_path, diary_path))


if __name__ == "__main__":
    main()
