"""
Tool definitions with error handling and validation.
All tools follow the function_tool decorator pattern.
"""

from typing import Dict, Any
from agents import function_tool
import logging
from src.utils.logger import setup_logging
from src.models.responses import QueryKnowledgeBaseInput, UpdateRecordInput
from src.utils.constants import KNOWLEDGE_BASE

logger = setup_logging(__name__)


# In-memory database (can be replaced with actual DB)
_mock_records: Dict[str, str] = {}


@function_tool
def query_knowledge_base(topic: str) -> str:
    """
    Search internal documentation for policies and procedures.
    
    Args:
        topic: Policy topic to search for (e.g., 'refund', 'shipping')
        
    Returns:
        Policy information or not found message
        
    Raises:
        ValueError: If topic is invalid
        
    Example:
        >>> query_knowledge_base("refund")
        "Refunds require an original receipt..."
    """
    try:
        # Validate input
        validated_input = QueryKnowledgeBaseInput(topic=topic)
        logger.debug(f"Querying knowledge base for topic: {validated_input.topic}")
        
        result = KNOWLEDGE_BASE.get(
            validated_input.topic,
            f"Policy for '{topic}' not found in knowledge base."
        )
        
        logger.info(f"Successfully retrieved policy for: {validated_input.topic}")
        return result
        
    except ValueError as e:
        error_msg = f"Invalid input for knowledge base query: {e}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error querying knowledge base: {e}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"


@function_tool
def update_record(record_id: str, status: str) -> str:
    """
    Update system records with new status.
    
    Args:
        record_id: ID of the record to update
        status: New status value
        
    Returns:
        Success or error message
        
    Raises:
        ValueError: If record_id or status is invalid
        
    Example:
        >>> update_record("ticket-123", "Resolved")
        "SUCCESS: Record ticket-123 updated to status: Resolved"
    """
    try:
        # Validate inputs
        validated_input = UpdateRecordInput(record_id=record_id, status=status)
        logger.debug(f"Updating record: {validated_input.record_id} to {validated_input.status}")
        
        # Update mock database
        _mock_records[validated_input.record_id] = validated_input.status
        
        success_msg = f"SUCCESS: Record {validated_input.record_id} has been updated to status: {validated_input.status}."
        logger.info(success_msg)
        
        return success_msg
        
    except ValueError as e:
        error_msg = f"Invalid input for record update: {e}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error updating record: {e}"
        logger.error(error_msg)
        return f"ERROR: {error_msg}"


def get_record_status(record_id: str) -> str:
    """
    Get the current status of a record (helper function, not a tool).
    
    Args:
        record_id: ID of the record to check
        
    Returns:
        Current status or "Not found" message
    """
    return _mock_records.get(record_id, "Record not found")


def clear_mock_db() -> None:
    """Clear the mock database (useful for testing)."""
    global _mock_records
    _mock_records.clear()
    logger.debug("Mock database cleared")
