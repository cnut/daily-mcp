"""Tests for daily log tools."""

from pathlib import Path

from daily_mcp.db import Database
from daily_mcp.tools import daily_log


class TestAddDailyLog:
    """Tests for add_daily_log function."""

    def test_add_log_basic(self, temp_db: Database, temp_log_dir: Path) -> None:
        """Test basic log entry."""
        result = daily_log.add_daily_log(temp_db, content="Had a great day")
        assert "Logged entry" in result

    def test_add_log_with_date(self, temp_db: Database, temp_log_dir: Path) -> None:
        """Test log entry with specific date."""
        result = daily_log.add_daily_log(temp_db, content="Past event", date="2024-01-15")
        assert "2024-01-15" in result

        # Verify file was created
        log_file = temp_log_dir / "2024-01-15.json"
        assert log_file.exists()


class TestSearchDailyLog:
    """Tests for search_daily_log function."""

    def test_search_empty(self, temp_db: Database, temp_log_dir: Path) -> None:
        """Test search on empty logs."""
        result = daily_log.search_daily_log(temp_db)
        assert "No matching" in result

    def test_search_with_data(self, temp_db: Database, temp_log_dir: Path) -> None:
        """Test search with data."""
        daily_log.add_daily_log(temp_db, content="Morning run")
        daily_log.add_daily_log(temp_db, content="Lunch meeting")

        result = daily_log.search_daily_log(temp_db)
        assert "Morning run" in result
        assert "Lunch meeting" in result

    def test_search_by_keyword(self, temp_db: Database, temp_log_dir: Path) -> None:
        """Test search by keyword."""
        daily_log.add_daily_log(temp_db, content="Morning run")
        daily_log.add_daily_log(temp_db, content="Lunch meeting")

        result = daily_log.search_daily_log(temp_db, keyword="run")
        assert "Morning run" in result
        assert "Lunch meeting" not in result

    def test_search_by_date_range(self, temp_db: Database, temp_log_dir: Path) -> None:
        """Test search by date range."""
        daily_log.add_daily_log(temp_db, content="Jan event", date="2024-01-15")
        daily_log.add_daily_log(temp_db, content="Feb event", date="2024-02-15")

        result = daily_log.search_daily_log(temp_db, start_date="2024-01-01", end_date="2024-01-31")
        assert "Jan event" in result
        assert "Feb event" not in result
