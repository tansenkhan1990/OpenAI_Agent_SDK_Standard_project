from pydantic import BaseModel, Field
from typing import Literal

class TransactionResult(BaseModel):
    """Industry Standard: Using Pydantic for Guaranteed Output Structure."""
    transaction_id: str = Field(..., description="Unique UUID for the request")
    status: Literal["success", "denied", "flagged"] = Field(..., description="The final state of the request")
    amount_processed: float = Field(default=0.0, ge=0)
    summary: str = Field(..., description="A brief professional summary for the client")