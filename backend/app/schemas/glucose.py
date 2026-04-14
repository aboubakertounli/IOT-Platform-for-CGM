"""Pydantic schema for validating incoming CGM glucose readings."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class GlucoseReading(BaseModel):
    """Validated glucose measurement received from MQTT."""

    device_id: str = Field(..., min_length=1, examples=["DEX-G6-001"])
    patient_id: str = Field(..., min_length=1, examples=["PAT-001"])
    timestamp: datetime
    glucose_mg_dl: float = Field(..., gt=0, lt=1000)
    unit: str = Field(default="mg/dL")
    sequence_number: int = Field(..., ge=0)

    @field_validator("unit")
    @classmethod
    def unit_must_be_known(cls, v: str) -> str:
        allowed = {"mg/dL", "mmol/L"}
        if v not in allowed:
            raise ValueError(f"unit must be one of {allowed}, got '{v}'")
        return v
