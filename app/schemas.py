from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ReviewRequest(BaseModel):
    decision: str
    note: str = ""
    corrections: dict[str, Any] | None = None


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    document_type: str
    status: str
    confidence: float
    summary: str
    extracted_data: dict[str, Any]
    reviewer_note: str | None
    created_at: datetime
    reviewed_at: datetime | None
