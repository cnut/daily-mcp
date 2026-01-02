"""Tests for finance tools."""

from daily_mcp.db import Database
from daily_mcp.tools import finance


class TestRecordExpense:
    """Tests for record_expense function."""

    def test_record_expense_basic(self, temp_db: Database) -> None:
        """Test basic expense recording."""
        result = finance.record_expense(temp_db, amount=100.0, category="food")
        assert "Recorded expense" in result
        assert "100" in result
        assert "food" in result

    def test_record_expense_with_note(self, temp_db: Database) -> None:
        """Test expense recording with note."""
        result = finance.record_expense(temp_db, amount=50.0, category="transport", note="taxi")
        assert "taxi" in result

    def test_record_expense_with_date(self, temp_db: Database) -> None:
        """Test expense recording with specific datetime."""
        result = finance.record_expense(
            temp_db, amount=200.0, category="shopping", datetime_str="2024-01-15 10:30:00"
        )
        assert "Recorded expense" in result

        # Verify in database
        rows = temp_db.fetchall("SELECT * FROM finance WHERE datetime = '2024-01-15 10:30:00'")
        assert len(rows) == 1


class TestRecordIncome:
    """Tests for record_income function."""

    def test_record_income_basic(self, temp_db: Database) -> None:
        """Test basic income recording."""
        result = finance.record_income(temp_db, amount=5000.0, source="salary")
        assert "Recorded income" in result
        assert "5000" in result
        assert "salary" in result


class TestQueryFinance:
    """Tests for query_finance function."""

    def test_query_finance_empty(self, temp_db: Database) -> None:
        """Test query on empty database."""
        result = finance.query_finance(temp_db, "SELECT * FROM finance")
        assert "No results" in result

    def test_query_finance_with_data(self, temp_db: Database) -> None:
        """Test query with data."""
        finance.record_expense(temp_db, amount=100.0, category="food")
        finance.record_income(temp_db, amount=1000.0, source="salary")

        result = finance.query_finance(temp_db, "SELECT * FROM finance")
        assert "food" in result
        assert "salary" in result

    def test_query_finance_non_select(self, temp_db: Database) -> None:
        """Test that non-SELECT queries are rejected."""
        result = finance.query_finance(temp_db, "DELETE FROM finance")
        assert "Error" in result
        assert "SELECT" in result

    def test_query_finance_wrong_table(self, temp_db: Database) -> None:
        """Test that queries on wrong table are rejected."""
        result = finance.query_finance(temp_db, "SELECT * FROM users")
        assert "Error" in result
        assert "finance" in result
