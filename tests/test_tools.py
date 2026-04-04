"""
Unit tests for tools module.
Tests tool validation and error handling.
"""

import pytest
from src.tools.knowledge_base import (
    query_knowledge_base,
    update_record,
    get_record_status,
    clear_database,
)


class TestQueryKnowledgeBase:
    """Tests for query_knowledge_base tool."""
    
    def test_valid_query(self):
        """Test querying with valid topic."""
        result = query_knowledge_base("refund")
        assert "Refunds require" in result
    
    def test_query_case_insensitive(self):
        """Test that queries are case-insensitive."""
        result_lower = query_knowledge_base("refund")
        result_upper = query_knowledge_base("REFUND")
        assert result_lower == result_upper
    
    def test_query_nonexistent_topic(self):
        """Test querying for non-existent topic."""
        result = query_knowledge_base("nonexistent")
        assert "not found" in result.lower()
    
    def test_query_all_topics(self):
        """Test that all known topics return results."""
        topics = ["refund", "shipping", "return", "warranty", "cancellation"]
        for topic in topics:
            result = query_knowledge_base(topic)
            assert "ERROR" not in result


class TestUpdateRecord:
    """Tests for update_record tool."""
    
    def setup_method(self):
        """Clear database before each test."""
        clear_database()
    
    def test_valid_update(self):
        """Test updating a record."""
        result = update_record("ticket-001", "Resolved")
        assert "SUCCESS" in result
        assert "ticket-001" in result
    
    def test_update_creates_record(self):
        """Test that update modifies existing record in DB."""
        # ticket-001 should exist in database
        result = update_record("ticket-001", "In-Progress")
        assert "SUCCESS" in result
        
        # Verify status was updated
        status = get_record_status("ticket-001")
        assert status == "In-Progress"
    
    def test_update_overwrites_status(self):
        """Test that updating overwrites previous status."""
        update_record("ticket-002", "Escalated")
        status = get_record_status("ticket-002")
        assert status == "Escalated"
        
        # Update again
        update_record("ticket-002", "Resolved")
        status = get_record_status("ticket-002")
        assert status == "Resolved"
    
    def teardown_method(self):
        """Clean up after tests."""
        clear_database()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
