"""
Data models using Pydantic for type safety and validation.
Follows industry standard practices for structured data.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, List, Optional
import uuid
from datetime import datetime
from src.utils.constants import STATUS_RESOLVED, STATUS_IN_PROGRESS, STATUS_ESCALATED


class AgentResponse(BaseModel):
    """
    Structured output format for agent responses.
    Enforces schema for all agent outputs.
    """
    ticket_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique ticket identifier"
    )
    status: Literal["Resolved", "In-Progress", "Escalated"] = Field(
        description="Current status of the request"
    )
    summary: str = Field(
        description="Summary of actions taken"
    )
    next_steps: List[str] = Field(
        default_factory=list,
        description="List of remaining actions needed"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when response was created"
    )
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is one of allowed values."""
        allowed = [STATUS_RESOLVED, STATUS_IN_PROGRESS, STATUS_ESCALATED]
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v
    
    @field_validator("summary")
    @classmethod
    def validate_summary(cls, v: str) -> str:
        """Validate summary is not empty."""
        if not v or not v.strip():
            raise ValueError("Summary cannot be empty")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "Resolved",
                "summary": "Customer refund processed successfully",
                "next_steps": ["Send confirmation email"],
                "created_at": "2025-04-04T10:30:00"
            }
        }


class ToolInput(BaseModel):
    """Base class for tool inputs with validation."""
    
    class Config:
        validate_assignment = True


class QueryKnowledgeBaseInput(ToolInput):
    """Input validation for query_knowledge_base tool."""
    topic: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Topic to search for in knowledge base"
    )
    
    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Validate topic input."""
        if not v.strip():
            raise ValueError("Topic cannot be empty or whitespace")
        return v.lower().strip()


class UpdateRecordInput(ToolInput):
    """Input validation for update_record tool."""
    record_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Record ID to update"
    )
    status: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="New status for the record"
    )
    
    @field_validator("record_id", "status")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Validate fields are not empty."""
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()


class ErrorResponse(BaseModel):
    """Structured error response format."""
    error_code: str = Field(description="Error code for categorization")
    message: str = Field(description="Error message")
    details: Optional[dict] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "AGENT_TIMEOUT",
                "message": "Agent execution exceeded timeout limit",
                "details": {"timeout_seconds": 30},
                "timestamp": "2025-04-04T10:30:00"
            }
        }
