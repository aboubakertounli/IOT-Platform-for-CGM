"""Service layer for glucose measurement operations."""

from datetime import datetime
from typing import Literal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.glucose_measurement import GlucoseMeasurement
from app.repositories import glucose_repository as glucose_repo
from app.repositories import patient_repository as patient_repo
from app.schemas.glucose import (
    GlucoseHistoryResponse,
    GlucoseMeasurementResponse,
    GlucoseStatsResponse,
)


def _to_response(m: GlucoseMeasurement, patient_id_str: str) -> GlucoseMeasurementResponse:
    return GlucoseMeasurementResponse(
        id=m.id,
        patient_id=patient_id_str,
        device_id=m.device.device_id,
        timestamp=m.timestamp,
        glucose_mg_dl=m.glucose_mg_dl,
        unit=m.unit,
        sequence_number=m.sequence_number,
        created_at=m.created_at,
    )


async def _resolve_patient(session: AsyncSession, patient_id: str):
    """Lookup patient or raise 404."""
    patient = await patient_repo.get_by_patient_id(session, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    return patient


async def get_latest(
    session: AsyncSession,
    patient_id: str,
) -> GlucoseMeasurementResponse:
    patient = await _resolve_patient(session, patient_id)
    measurement = await glucose_repo.get_latest_by_patient(session, patient.id)
    if measurement is None:
        raise HTTPException(
            status_code=404,
            detail=f"No measurements found for patient {patient_id}",
        )
    return _to_response(measurement, patient_id)


async def get_history(
    session: AsyncSession,
    patient_id: str,
    limit: int = 100,
    offset: int = 0,
    from_ts: datetime | None = None,
    to_ts: datetime | None = None,
    order: Literal["asc", "desc"] = "desc",
) -> GlucoseHistoryResponse:
    patient = await _resolve_patient(session, patient_id)
    measurements = await glucose_repo.get_history_by_patient(
        session, patient.id, limit, offset, from_ts, to_ts, order,
    )
    return GlucoseHistoryResponse(
        patient_id=patient_id,
        count=len(measurements),
        measurements=[_to_response(m, patient_id) for m in measurements],
    )


async def get_stats(
    session: AsyncSession,
    patient_id: str,
) -> GlucoseStatsResponse:
    patient = await _resolve_patient(session, patient_id)
    row = await glucose_repo.get_stats_by_patient(session, patient.id)
    return GlucoseStatsResponse(
        patient_id=patient_id,
        count=row.count,
        min_glucose=float(row.min_glucose) if row.min_glucose is not None else None,
        max_glucose=float(row.max_glucose) if row.max_glucose is not None else None,
        avg_glucose=float(row.avg_glucose) if row.avg_glucose is not None else None,
        latest_timestamp=row.latest_timestamp,
    )
