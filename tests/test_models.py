"""
Unit tests for models and input validation.
Demonstrates testing best practices for Agentic AI.
"""

import pytest
from src.models.responses import (
    AgentResponse,
    QueryKnowledgeBaseInput,
    UpdateRecordInput,
    ErrorResponse,
)


class TestAgentResponse:
    """Tests for AgentResponse model."""
    
    def test_valid_response(self):
        """Test creating a valid agent response."""
        response = AgentResponse(
            status="Resolved",
            summary="Task completed successfully"
        )
        assert response.status == "Resolved"
        assert response.summary == "Task completed successfully"
        assert response.ticket_id is not None
    
    def test_invalid_status(self):
        """Test that invalid status raises error."""
        with pytest.raises(ValueError):
            AgentResponse(
                status="Invalid",
                summary="Test"
            )
    
    def test_empty_summary(self):
        """Test that empty summary raises error."""
        with pytest.raises(ValueError):
            AgentResponse(
                status="Resolved",
                summary=""
            )
    
    def test_next_steps(self):
        """Test response with next steps."""
        response = AgentResponse(
            status="In-Progress",
            summary="Task started",
            next_steps=["Step 1", "Step 2"]
        )
        assert len(response.next_steps) == 2


class TestQueryKnowledgeBaseInput:
    """Tests for QueryKnowledgeBaseInput model."""
    
    def test_valid_input(self):
        """Test creating valid input."""
        input_data = QueryKnowledgeBaseInput(topic="refund")
        assert input_data.topic == "refund"
    
    def test_topic_lowercased(self):
        """Test that topic is converted to lowercase."""
        input_data = QueryKnowledgeBaseInput(topic="REFUND")
        assert input_data.topic == "refund"
    
    def test_empty_topic(self):
        """Test that empty topic raises error."""
        with pytest.raises(ValueError):
            QueryKnowledgeBaseInput(topic="")
    
    def test_topic_too_long(self):
        """Test that very long topic raises error."""
        with pytest.raises(ValueError):
            QueryKnowledgeBaseInput(topic="x" * 101)


class TestUpdateRecordInput:
    """Tests for UpdateRecordInput model."""
    
    def test_valid_input(self):
        """Test creating valid input."""
        input_data = UpdateRecordInput(record_id="ticket-123", status="Resolved")
        assert input_data.record_id == "ticket-123"
        assert input_data.status == "Resolved"
    
    def test_empty_record_id(self):
        """Test that empty record_id raises error."""
        with pytest.raises(ValueError):
            UpdateRecordInput(record_id="", status="Resolved")
    
    def test_empty_status(self):
        """Test that empty status raises error."""
        with pytest.raises(ValueError):
            UpdateRecordInput(record_id="ticket-123", status="")


class TestErrorResponse:
    """Tests for ErrorResponse model."""
    
    def test_valid_error(self):
        """Test creating valid error response."""
        error = ErrorResponse(
            error_code="AGENT_TIMEOUT",
            message="Agent execution timed out"
        )
        assert error.error_code == "AGENT_TIMEOUT"
        assert error.timestamp is not None
    
    def test_error_with_details(self):
        """Test error response with additional details."""
        error = ErrorResponse(
            error_code="AGENT_ERROR",
            message="Error occurred",
            details={"timeout": 30}
        )
        assert error.details == {"timeout": 30}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
