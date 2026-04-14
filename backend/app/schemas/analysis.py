"""Schemas for glucose analysis results."""

from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel

from app.core.enums import GlucoseClassification, TrendDirection


@dataclass
class AnalysisResult:
    """Internal result of glucose analysis (not an API schema)."""

    classification: GlucoseClassification
    trend_direction: TrendDirection
    trend_rate: float
    is_anomaly: bool
    anomaly_score: float


class AnalysisResultResponse(BaseModel):
    """API response for the latest analysis of a patient."""

    patient_id: str
    measurement_id: int
    timestamp: datetime
    glucose_mg_dl: float
    classification: str
    trend_direction: str
    trend_rate_mg_dl_per_min: float
    is_anomaly: bool
    anomaly_score: float
