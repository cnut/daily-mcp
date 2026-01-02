"""Tests for health tools."""

from daily_mcp.db import Database
from daily_mcp.tools import health


class TestRecordHealth:
    """Tests for record_health function."""

    def test_record_blood_pressure(self, temp_db: Database) -> None:
        """Test recording blood pressure."""
        result = health.record_health(temp_db, metric_type="blood_pressure", value="120/80")
        assert "Blood Pressure" in result
        assert "120/80" in result
        assert "mmHg" in result

    def test_record_weight(self, temp_db: Database) -> None:
        """Test recording weight."""
        result = health.record_health(temp_db, metric_type="weight", value="70")
        assert "Weight" in result
        assert "70" in result
        assert "kg" in result

    def test_record_with_custom_unit(self, temp_db: Database) -> None:
        """Test recording with custom unit."""
        result = health.record_health(temp_db, metric_type="weight", value="154", unit="lbs")
        assert "lbs" in result

    def test_record_with_note(self, temp_db: Database) -> None:
        """Test recording with note."""
        result = health.record_health(
            temp_db,
            metric_type="blood_pressure",
            value="130/85",
            note="after exercise",
        )
        assert "after exercise" in result


class TestQueryHealth:
    """Tests for query_health function."""

    def test_query_health_empty(self, temp_db: Database) -> None:
        """Test query on empty database."""
        result = health.query_health(temp_db)
        assert "No health records" in result

    def test_query_health_with_data(self, temp_db: Database) -> None:
        """Test query with data."""
        health.record_health(temp_db, metric_type="weight", value="70")
        health.record_health(temp_db, metric_type="heart_rate", value="72")

        result = health.query_health(temp_db)
        assert "70" in result
        assert "72" in result

    def test_query_health_by_type(self, temp_db: Database) -> None:
        """Test filtering by metric type."""
        health.record_health(temp_db, metric_type="weight", value="70")
        health.record_health(temp_db, metric_type="heart_rate", value="72")

        result = health.query_health(temp_db, metric_type="weight")
        assert "70" in result
        assert "72" not in result

    def test_query_health_with_sql(self, temp_db: Database) -> None:
        """Test direct SQL query."""
        health.record_health(temp_db, metric_type="weight", value="70")

        result = health.query_health(
            temp_db, sql="SELECT value FROM health WHERE metric_type = 'weight'"
        )
        assert "70" in result

    def test_query_health_sql_non_select(self, temp_db: Database) -> None:
        """Test that non-SELECT SQL is rejected."""
        result = health.query_health(temp_db, sql="DELETE FROM health")
        assert "Error" in result
