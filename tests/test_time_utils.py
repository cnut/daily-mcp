"""Tests for time utilities."""

from datetime import datetime

from daily_mcp.tools.time_utils import get_current_time


class TestGetCurrentTime:
    """Tests for get_current_time function."""

    def test_get_current_time_returns_string(self) -> None:
        """Test that get_current_time returns a non-empty string."""
        result = get_current_time()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_current_time_contains_date(self) -> None:
        """Test that result contains current date."""
        result = get_current_time()
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in result

    def test_get_current_time_contains_sections(self) -> None:
        """Test that result contains expected sections."""
        result = get_current_time()
        assert "Current Time Information:" in result
        assert "Now:" in result
        assert "Date:" in result
        assert "Time:" in result
        assert "Yesterday:" in result

    def test_get_current_time_contains_examples(self) -> None:
        """Test that result contains usage examples."""
        result = get_current_time()
        assert "just now" in result
        assert "yesterday" in result
