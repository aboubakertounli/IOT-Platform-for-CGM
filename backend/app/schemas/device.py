"""Pydantic response schemas for devices."""

from datetime import datetime

from pydantic import BaseModel


class DeviceResponse(BaseModel):
    id: int
    device_id: str
    patient_id: str
    status: str
    created_at: datetime
