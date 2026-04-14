"""Pydantic response schemas for patients."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: str
    first_name: str | None
    last_name: str | None
    created_at: datetime
