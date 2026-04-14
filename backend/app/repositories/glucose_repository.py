"""Repository for glucose data.

Ingestion helpers: ensure_patient, ensure_device (used by IngestionService).
API read queries: get_latest_by_patient, get_history_by_patient, etc.
Analysis query: get_recent_for_analysis.
"""

import logging
from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Literal

from sqlalchemy import Row, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.device import Device
from app.models.glucose_measurement import GlucoseMeasurement
from app.models.patient import Patient

logger = logging.getLogger(__name__)


# ── Ingestion helpers ─────────────────────────────


async def ensure_patient(session: AsyncSession, patient_id: str) -> int:
    """Return PK for the given patient_id, inserting if new."""
    await session.execute(
        pg_insert(Patient)
        .values(patient_id=patient_id)
        .on_conflict_do_nothing(index_elements=["patient_id"])
    )
    result = await session.execute(
        select(Patient.id).where(Patient.patient_id == patient_id)
    )
    return result.scalar_one()


async def ensure_device(session: AsyncSession, device_id: str, patient_pk: int) -> int:
    """Return PK for the given device_id, inserting if new."""
    await session.execute(
        pg_insert(Device)
        .values(device_id=device_id, patient_id=patient_pk)
        .on_conflict_do_nothing(index_elements=["device_id"])
    )
    result = await session.execute(
        select(Device.id).where(Device.device_id == device_id)
    )
    return result.scalar_one()


# ── Analysis query ────────────────────────────────


async def get_recent_for_analysis(
    session: AsyncSession,
    patient_pk: int,
    before: datetime,
    hours: int = 24,
    limit: int = 500,
) -> Sequence[GlucoseMeasurement]:
    """Get recent measurements for a patient before a given timestamp.

    Returns measurements ordered chronologically (ascending).
    Used by the analysis service for trend and anomaly detection.
    """
    cutoff = before - timedelta(hours=hours)
    result = await session.execute(
        select(GlucoseMeasurement)
        .where(
            GlucoseMeasurement.patient_id == patient_pk,
            GlucoseMeasurement.timestamp >= cutoff,
            GlucoseMeasurement.timestamp < before,
        )
        .order_by(GlucoseMeasurement.timestamp.asc())
        .limit(limit)
    )
    return result.scalars().all()


# ── API read queries ──────────────────────────────


async def get_latest_by_patient(
    session: AsyncSession,
    patient_pk: int,
) -> GlucoseMeasurement | None:
    result = await session.execute(
        select(GlucoseMeasurement)
        .options(selectinload(GlucoseMeasurement.device))
        .where(GlucoseMeasurement.patient_id == patient_pk)
        .order_by(GlucoseMeasurement.timestamp.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_history_by_patient(
    session: AsyncSession,
    patient_pk: int,
    limit: int = 100,
    offset: int = 0,
    from_ts: datetime | None = None,
    to_ts: datetime | None = None,
    order: Literal["asc", "desc"] = "desc",
) -> Sequence[GlucoseMeasurement]:
    stmt = (
        select(GlucoseMeasurement)
        .options(selectinload(GlucoseMeasurement.device))
        .where(GlucoseMeasurement.patient_id == patient_pk)
    )
    if from_ts is not None:
        stmt = stmt.where(GlucoseMeasurement.timestamp >= from_ts)
    if to_ts is not None:
        stmt = stmt.where(GlucoseMeasurement.timestamp <= to_ts)

    order_col = (
        GlucoseMeasurement.timestamp.asc()
        if order == "asc"
        else GlucoseMeasurement.timestamp.desc()
    )
    stmt = stmt.order_by(order_col).offset(offset).limit(limit)

    result = await session.execute(stmt)
    return result.scalars().all()


async def get_stats_by_patient(session: AsyncSession, patient_pk: int) -> Row:
    result = await session.execute(
        select(
            func.count().label("count"),
            func.min(GlucoseMeasurement.glucose_mg_dl).label("min_glucose"),
            func.max(GlucoseMeasurement.glucose_mg_dl).label("max_glucose"),
            func.round(func.avg(GlucoseMeasurement.glucose_mg_dl), 2).label("avg_glucose"),
            func.max(GlucoseMeasurement.timestamp).label("latest_timestamp"),
        ).where(GlucoseMeasurement.patient_id == patient_pk)
    )
    return result.one()
