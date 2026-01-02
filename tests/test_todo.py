"""Tests for todo tools."""

from daily_mcp.db import Database
from daily_mcp.tools import todo


class TestAddTodo:
    """Tests for add_todo function."""

    def test_add_todo_basic(self, temp_db: Database) -> None:
        """Test basic todo creation."""
        result = todo.add_todo(temp_db, content="Buy milk")
        assert "Added todo" in result
        assert "Buy milk" in result

    def test_add_todo_with_topic(self, temp_db: Database) -> None:
        """Test todo with topic."""
        result = todo.add_todo(temp_db, content="Finish report", topic="work")
        assert "work" in result

    def test_add_todo_with_due_date(self, temp_db: Database) -> None:
        """Test todo with due date."""
        result = todo.add_todo(temp_db, content="Submit taxes", due_date="2024-04-15")
        assert "2024-04-15" in result


class TestCompleteTodo:
    """Tests for complete_todo function."""

    def test_complete_todo_by_id(self, temp_db: Database) -> None:
        """Test completing todo by ID."""
        todo.add_todo(temp_db, content="Test task")

        # Get the ID
        row = temp_db.fetchone("SELECT id FROM todo WHERE content = 'Test task'")
        todo_id = row[0]

        result = todo.complete_todo(temp_db, todo_id=todo_id)
        assert "Completed" in result
        assert "Test task" in result

    def test_complete_todo_by_content(self, temp_db: Database) -> None:
        """Test completing todo by content match."""
        todo.add_todo(temp_db, content="Buy groceries")

        result = todo.complete_todo(temp_db, content_match="groceries")
        assert "Completed" in result
        assert "groceries" in result

    def test_complete_todo_not_found(self, temp_db: Database) -> None:
        """Test completing non-existent todo."""
        result = todo.complete_todo(temp_db, todo_id=999)
        assert "Error" in result

    def test_complete_todo_no_params(self, temp_db: Database) -> None:
        """Test completing without parameters."""
        result = todo.complete_todo(temp_db)
        assert "Error" in result


class TestListTodos:
    """Tests for list_todos function."""

    def test_list_todos_empty(self, temp_db: Database) -> None:
        """Test listing empty todos."""
        result = todo.list_todos(temp_db)
        assert "No todos" in result

    def test_list_todos_with_items(self, temp_db: Database) -> None:
        """Test listing todos with items."""
        todo.add_todo(temp_db, content="Task 1")
        todo.add_todo(temp_db, content="Task 2")

        result = todo.list_todos(temp_db)
        assert "Task 1" in result
        assert "Task 2" in result

    def test_list_todos_filter_by_topic(self, temp_db: Database) -> None:
        """Test filtering by topic."""
        todo.add_todo(temp_db, content="Work task", topic="work")
        todo.add_todo(temp_db, content="Home task", topic="home")

        result = todo.list_todos(temp_db, topic="work")
        assert "Work task" in result
        assert "Home task" not in result

    def test_list_todos_filter_by_status(self, temp_db: Database) -> None:
        """Test filtering by status."""
        todo.add_todo(temp_db, content="Pending task")
        todo.add_todo(temp_db, content="Done task")

        # Complete one task
        row = temp_db.fetchone("SELECT id FROM todo WHERE content = 'Done task'")
        todo.complete_todo(temp_db, todo_id=row[0])

        result = todo.list_todos(temp_db, status="completed")
        assert "Done task" in result
        assert "Pending task" not in result
