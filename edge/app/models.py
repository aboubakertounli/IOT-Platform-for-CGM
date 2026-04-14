from datetime import datetime

from pydantic import BaseModel, Field


class GlucoseReading(BaseModel):
    """Single CGM glucose measurement published to MQTT."""

    device_id: str = Field(..., examples=["DEX-G6-001"])
    patient_id: str = Field(..., examples=["PAT-001"])
    timestamp: datetime
    glucose_mg_dl: float
    unit: str = "mg/dL"
    sequence_number: int = Field(..., ge=0)
