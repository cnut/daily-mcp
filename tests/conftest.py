"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest

from daily_mcp.db import Database


@pytest.fixture
def temp_db() -> Database:
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db = Database(f.name)
        db.init()
        yield db
        db.close()
        Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def temp_log_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a temporary log directory for testing."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    # Patch the log directory
    def mock_get_log_dir() -> Path:
        return log_dir

    monkeypatch.setattr("daily_mcp.tools.daily_log._get_log_dir", mock_get_log_dir)
    return log_dir
