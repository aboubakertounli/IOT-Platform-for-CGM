"""Glucose measurement endpoints."""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.glucose import (
    GlucoseHistoryResponse,
    GlucoseMeasurementResponse,
    GlucoseStatsResponse,
)
from app.services import glucose_service

router = APIRouter(prefix="/api/glucose", tags=["glucose"])


@router.get("/{patient_id}/latest", response_model=GlucoseMeasurementResponse)
async def get_latest(patient_id: str, db: AsyncSession = Depends(get_db)):
    return await glucose_service.get_latest(db, patient_id)


@router.get("/{patient_id}/history", response_model=GlucoseHistoryResponse)
async def get_history(
    patient_id: str,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    from_ts: datetime | None = Query(default=None),
    to_ts: datetime | None = Query(default=None),
    order: Literal["asc", "desc"] = Query(default="desc"),
    db: AsyncSession = Depends(get_db),
):
    return await glucose_service.get_history(
        db, patient_id, limit, offset, from_ts, to_ts, order,
    )


@router.get("/{patient_id}/stats", response_model=GlucoseStatsResponse)
async def get_stats(patient_id: str, db: AsyncSession = Depends(get_db)):
    return await glucose_service.get_stats(db, patient_id)
