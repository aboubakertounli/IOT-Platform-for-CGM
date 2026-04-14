"""Pydantic schemas for glucose data.

GlucoseReading: MQTT input validation.
GlucoseMeasurementResponse / GlucoseStatsResponse / GlucoseHistoryResponse: API output.
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


# ── MQTT input ────────────────────────────────────

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


# ── API responses ─────────────────────────────────

class GlucoseMeasurementResponse(BaseModel):
    id: int
    patient_id: str
    device_id: str
    timestamp: datetime
    glucose_mg_dl: float
    unit: str
    sequence_number: int
    classification: str | None = None
    trend_direction: str | None = None
    trend_rate: float | None = None
    is_anomaly: bool | None = None
    anomaly_score: float | None = None
    created_at: datetime


class GlucoseStatsResponse(BaseModel):
    patient_id: str
    count: int
    min_glucose: float | None
    max_glucose: float | None
    avg_glucose: float | None
    latest_timestamp: datetime | None


class GlucoseHistoryResponse(BaseModel):
    patient_id: str
    count: int
    measurements: list[GlucoseMeasurementResponse]
