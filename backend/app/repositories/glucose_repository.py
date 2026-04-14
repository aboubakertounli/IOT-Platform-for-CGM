"""Repository for glucose-related persistence.

Handles patient/device upsert and measurement insertion.
Uses PostgreSQL ON CONFLICT for safe concurrent access.
"""

import logging

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

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
