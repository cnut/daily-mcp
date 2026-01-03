"""Tests for diary tools."""

from pathlib import Path

from daily_mcp.tools import diary


class TestAddDiary:
    """Tests for add_diary function."""

    def test_add_diary_basic(self, temp_diary_dir: Path) -> None:
        """Test basic diary entry."""
        result = diary.add_diary(temp_diary_dir, content="Had a great day")
        assert "Diary entry added" in result

    def test_add_diary_with_datetime(self, temp_diary_dir: Path) -> None:
        """Test diary entry with specific datetime."""
        result = diary.add_diary(
            temp_diary_dir, content="Past event", datetime_str="2024-01-15 10:30:00"
        )
        assert "2024-01-15 10:30:00" in result

        # Verify file was created in YYYY/MM/YYYY-MM-DD.md structure
        diary_file = temp_diary_dir / "2024" / "01" / "2024-01-15.md"
        assert diary_file.exists()

        # Verify markdown content
        content = diary_file.read_text(encoding="utf-8")
        assert "---" in content
        assert "date: 2024-01-15" in content
        assert "## 10:30" in content
        assert "Past event" in content

    def test_add_diary_with_tags(self, temp_diary_dir: Path) -> None:
        """Test diary entry with tags."""
        result = diary.add_diary(temp_diary_dir, content="Work meeting", tags=["work", "meeting"])
        assert "Diary entry added" in result
        assert "work" in result
        assert "meeting" in result

    def test_add_multiple_entries_same_day(self, temp_diary_dir: Path) -> None:
        """Test adding multiple entries on the same day."""
        diary.add_diary(
            temp_diary_dir,
            content="Morning entry",
            tags=["morning"],
            datetime_str="2024-01-15 08:00:00",
        )
        diary.add_diary(
            temp_diary_dir,
            content="Evening entry",
            tags=["evening"],
            datetime_str="2024-01-15 20:00:00",
        )

        diary_file = temp_diary_dir / "2024" / "01" / "2024-01-15.md"
        content = diary_file.read_text(encoding="utf-8")

        # Both entries should be in the file
        assert "## 08:00" in content
        assert "Morning entry" in content
        assert "## 20:00" in content
        assert "Evening entry" in content

        # Tags should be aggregated in frontmatter
        assert "morning" in content
        assert "evening" in content


class TestSearchDiary:
    """Tests for search_diary function."""

    def test_search_empty(self, temp_diary_dir: Path) -> None:
        """Test search on empty diary."""
        result = diary.search_diary(temp_diary_dir)
        assert "No matching" in result

    def test_search_with_data(self, temp_diary_dir: Path) -> None:
        """Test search with data."""
        diary.add_diary(temp_diary_dir, content="Morning run")
        diary.add_diary(temp_diary_dir, content="Lunch meeting")

        result = diary.search_diary(temp_diary_dir)
        assert "Morning run" in result
        assert "Lunch meeting" in result

    def test_search_by_keyword(self, temp_diary_dir: Path) -> None:
        """Test search by keyword."""
        diary.add_diary(temp_diary_dir, content="Morning run")
        diary.add_diary(temp_diary_dir, content="Lunch meeting")

        result = diary.search_diary(temp_diary_dir, keyword="run")
        assert "Morning run" in result
        assert "Lunch meeting" not in result

    def test_search_by_tag(self, temp_diary_dir: Path) -> None:
        """Test search by tag."""
        diary.add_diary(temp_diary_dir, content="Work task", tags=["work"])
        diary.add_diary(temp_diary_dir, content="Personal errand", tags=["personal"])

        result = diary.search_diary(temp_diary_dir, tag="work")
        assert "Work task" in result
        assert "Personal errand" not in result

    def test_search_by_datetime_range(self, temp_diary_dir: Path) -> None:
        """Test search by datetime range."""
        diary.add_diary(temp_diary_dir, content="Jan event", datetime_str="2024-01-15 10:00:00")
        diary.add_diary(temp_diary_dir, content="Feb event", datetime_str="2024-02-15 10:00:00")

        result = diary.search_diary(
            temp_diary_dir, start_datetime="2024-01-01", end_datetime="2024-01-31"
        )
        assert "Jan event" in result
        assert "Feb event" not in result


class TestLoadDiary:
    """Tests for _load_diary function."""

    def test_load_diary_parses_markdown(self, temp_diary_dir: Path) -> None:
        """Test that _load_diary correctly parses markdown format."""
        diary.add_diary(
            temp_diary_dir,
            content="Test content",
            tags=["test"],
            datetime_str="2024-01-15 14:30:00",
        )

        entries = diary._load_diary(temp_diary_dir, "2024-01-15")
        assert len(entries) == 1
        assert entries[0]["content"] == "Test content"
        assert entries[0]["datetime"] == "2024-01-15 14:30:00"
        assert "test" in entries[0]["tags"]
