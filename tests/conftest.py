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
def temp_diary_dir(tmp_path: Path) -> Path:
    """Create a temporary diary directory for testing."""
    diary_dir = tmp_path / "diary"
    diary_dir.mkdir()
    return diary_dir
