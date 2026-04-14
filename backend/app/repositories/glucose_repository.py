"""Repository for glucose data.

GlucoseRepository class: MQTT ingestion (owns session factory).
Module-level functions: API read queries (accept session parameter).
"""

import logging
from collections.abc import Sequence
from datetime import datetime
from typing import Literal

from sqlalchemy import Row, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from app.models.device import Device
from app.models.glucose_measurement import GlucoseMeasurement
from app.models.patient import Patient
from app.schemas.glucose import GlucoseReading

logger = logging.getLogger(__name__)


class GlucoseRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save_reading(self, reading: GlucoseReading) -> None:
        """Persist a validated glucose reading.

        Creates patient and device if they don't exist yet.
        """
        async with self._session_factory() as session:
            async with session.begin():
                patient_pk = await self._ensure_patient(session, reading.patient_id)
                device_pk = await self._ensure_device(session, reading.device_id, patient_pk)
                session.add(GlucoseMeasurement(
                    patient_id=patient_pk,
                    device_id=device_pk,
                    timestamp=reading.timestamp,
                    glucose_mg_dl=reading.glucose_mg_dl,
                    unit=reading.unit,
                    sequence_number=reading.sequence_number,
                ))

    async def count_measurements(self) -> int:
        async with self._session_factory() as session:
            result = await session.execute(
                select(func.count()).select_from(GlucoseMeasurement)
            )
            return result.scalar_one()

    async def _ensure_patient(self, session: AsyncSession, patient_id: str) -> int:
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

    async def _ensure_device(self, session: AsyncSession, device_id: str, patient_pk: int) -> int:
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
