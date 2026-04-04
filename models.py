from pydantic import BaseModel, Field
from typing import Literal, List
import uuid

class AgentResponse(BaseModel):
    ticket_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: Literal["Resolved", "In-Progress", "Escalated"]
    summary: str = Field(..., description="Summary of actions.")
    next_steps: List[str] = Field(default_factory=list)