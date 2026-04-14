"""Pydantic response schemas for alerts."""

from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    patient_id: str
    type: str
    severity: str
    message: str
    status: str
    created_at: datetime
    acknowledged_at: datetime | None
    resolved_at: datetime | None
