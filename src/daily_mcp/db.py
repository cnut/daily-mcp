"""Database module using SQLite (Python built-in)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from daily_mcp.logging import get_logger

logger = get_logger("db")


class Database:
    """SQLite database wrapper for daily-mcp."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        """
        Initialize database connection.

        Args:
            db_path: Path to database file. Defaults to ~/.daily-mcp/data.db
        """
        if db_path is None:
            data_dir = Path.home() / ".daily-mcp"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "data.db"

        self.db_path = str(db_path)
        self.conn: sqlite3.Connection | None = None

    def init(self) -> None:
        """Initialize database and create tables."""
        logger.info("Initializing database at %s", self.db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        logger.info("Database initialized successfully")

    def _create_tables(self) -> None:
        """Create all required tables."""
        if self.conn is None:
            msg = "Database not initialized"
            raise RuntimeError(msg)

        cursor = self.conn.cursor()

        # Finance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS finance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT,
                source TEXT,
                note TEXT,
                date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.debug("Finance table ready")

        # Todo table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                topic TEXT,
                status TEXT DEFAULT 'pending',
                due_date TEXT,
                completed_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.debug("Todo table ready")

        # Health table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT NOT NULL,
                value TEXT NOT NULL,
                unit TEXT,
                note TEXT,
                date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.debug("Health table ready")

        self.conn.commit()

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Cursor:
        """
        Execute SQL and return cursor.

        Args:
            sql: SQL statement
            params: Query parameters

        Returns:
            Cursor with results
        """
        if self.conn is None:
            msg = "Database not initialized"
            raise RuntimeError(msg)
        logger.debug("Executing SQL: %s", sql[:100])
        return self.conn.execute(sql, params)

    def fetchall(self, sql: str, params: tuple[Any, ...] = ()) -> list[Any]:
        """
        Execute SQL and fetch all results.

        Args:
            sql: SQL statement
            params: Query parameters

        Returns:
            List of rows
        """
        cursor = self.execute(sql, params)
        return cursor.fetchall()

    def fetchone(self, sql: str, params: tuple[Any, ...] = ()) -> Any:
        """
        Execute SQL and fetch one result.

        Args:
            sql: SQL statement
            params: Query parameters

        Returns:
            Single row or None
        """
        cursor = self.execute(sql, params)
        return cursor.fetchone()

    def commit(self) -> None:
        """Commit transaction."""
        if self.conn is None:
            msg = "Database not initialized"
            raise RuntimeError(msg)
        self.conn.commit()

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            logger.info("Closing database connection")
            self.conn.close()
            self.conn = None
