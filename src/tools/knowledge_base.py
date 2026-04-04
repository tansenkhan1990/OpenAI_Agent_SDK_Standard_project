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
from src.services.database import get_database

logger = setup_logging(__name__)


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
    Uses JSON database for persistent storage.
    
    Args:
        record_id: ID of the record to update (ticket or order)
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
        
        # Get database instance
        db = get_database()
        
        # Try to update ticket first, then record
        ticket_updated = db.update_ticket(validated_input.record_id, {"status": validated_input.status})
        
        if not ticket_updated:
            # Try updating as a record
            record_updated = db.update_record(validated_input.record_id, {"status": validated_input.status})
            
            if not record_updated:
                error_msg = f"Record not found: {validated_input.record_id}"
                logger.warning(error_msg)
                return f"ERROR: {error_msg}"
        
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
    Get the current status of a record or ticket.
    Helper function, not a tool.
    
    Args:
        record_id: ID of the record to check
        
    Returns:
        Current status or "Not found" message
    """
    try:
        db = get_database()
        
        # Try ticket first
        ticket = db.get_ticket(record_id)
        if ticket:
            return ticket.get("status", "Unknown")
        
        # Try record
        record = db.get_record(record_id)
        if record:
            return record.get("status", "Unknown")
        
        return "Record not found"
        
    except Exception as e:
        logger.error(f"Error getting record status: {e}")
        return "Error retrieving status"


def clear_database() -> None:
    """
    Clear the database (useful for testing).
    Only use in testing environments!
    """
    try:
        db = get_database()
        db.clear_database()
        logger.debug("Database cleared")
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
