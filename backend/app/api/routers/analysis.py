"""Analysis endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.repositories import glucose_repository as glucose_repo
from app.repositories import patient_repository as patient_repo
from app.schemas.analysis import AnalysisResultResponse

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/{patient_id}/latest", response_model=AnalysisResultResponse)
async def get_latest_analysis(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
):
    patient = await patient_repo.get_by_patient_id(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")

    measurement = await glucose_repo.get_latest_by_patient(db, patient.id)
    if measurement is None:
        raise HTTPException(
            status_code=404,
            detail=f"No measurements found for patient {patient_id}",
        )

    return AnalysisResultResponse(
        patient_id=patient_id,
        measurement_id=measurement.id,
        timestamp=measurement.timestamp,
        glucose_mg_dl=measurement.glucose_mg_dl,
        classification=measurement.classification or "unknown",
        trend_direction=measurement.trend_direction or "stable",
        trend_rate_mg_dl_per_min=measurement.trend_rate or 0.0,
        is_anomaly=measurement.is_anomaly or False,
        anomaly_score=measurement.anomaly_score or 0.0,
    )
