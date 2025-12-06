from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    """
    Standard error response model.
    """
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    remediation: Optional[str] = Field(None, description="Suggested remediation steps")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
