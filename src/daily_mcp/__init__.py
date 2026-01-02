"""Daily MCP - Personal daily life recording server."""

from daily_mcp.logging import get_logger, setup_logging
from daily_mcp.server import main

__version__ = "0.1.0"
__all__ = ["__version__", "get_logger", "main", "setup_logging"]
