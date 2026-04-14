"""Queries for patient-specific glucose thresholds with config fallback."""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.glucose_threshold import GlucoseThreshold


@dataclass
class ThresholdValues:
    """Resolved thresholds for a patient (DB or defaults)."""

    hypo_critical: float
    hypo_warning: float
    hyper_warning: float
    hyper_critical: float
    trend_rate_warning: float


async def get_for_patient(session: AsyncSession, patient_pk: int) -> ThresholdValues:
    """Return patient-specific thresholds, falling back to config defaults."""
    result = await session.execute(
        select(GlucoseThreshold).where(GlucoseThreshold.patient_id == patient_pk)
    )
    row = result.scalar_one_or_none()
    if row is not None:
        return ThresholdValues(
            hypo_critical=row.hypo_critical_mg_dl,
            hypo_warning=row.hypo_warning_mg_dl,
            hyper_warning=row.hyper_warning_mg_dl,
            hyper_critical=row.hyper_critical_mg_dl,
            trend_rate_warning=row.trend_rate_warning,
        )

    s = get_settings()
    return ThresholdValues(
        hypo_critical=s.GLUCOSE_HYPO_CRITICAL,
        hypo_warning=s.GLUCOSE_HYPO_WARNING,
        hyper_warning=s.GLUCOSE_HYPER_WARNING,
        hyper_critical=s.GLUCOSE_HYPER_CRITICAL,
        trend_rate_warning=s.GLUCOSE_TREND_RATE_WARNING,
    )
