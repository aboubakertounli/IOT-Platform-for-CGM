"""Alert endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.alert import Alert
from app.repositories import alert_repository as alert_repo
from app.repositories import patient_repository as patient_repo
from app.schemas.alert import AlertResponse

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


def _to_response(a: Alert) -> AlertResponse:
    return AlertResponse(
        id=a.id,
        patient_id=a.patient.patient_id,
        type=a.type,
        severity=a.severity,
        message=a.message,
        status=a.status,
        created_at=a.created_at,
        acknowledged_at=a.acknowledged_at,
        resolved_at=a.resolved_at,
    )


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    alerts = await alert_repo.list_all(db, limit, offset)
    return [_to_response(a) for a in alerts]


@router.get("/{patient_id}", response_model=list[AlertResponse])
async def get_alerts_by_patient(
    patient_id: str,
    limit: int = Query(default=100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    patient = await patient_repo.get_by_patient_id(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    alerts = await alert_repo.get_by_patient(db, patient.id, limit)
    return [_to_response(a) for a in alerts]


@router.get("/{patient_id}/active", response_model=list[AlertResponse])
async def get_active_alerts(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
):
    patient = await patient_repo.get_by_patient_id(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    alerts = await alert_repo.get_active_by_patient(db, patient.id)
    return [_to_response(a) for a in alerts]


@router.put("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
):
    alert = await alert_repo.acknowledge(db, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    return _to_response(alert)
