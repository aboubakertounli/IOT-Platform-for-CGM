"""Read-only queries for devices."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.device import Device
from app.models.patient import Patient


async def list_all(session: AsyncSession) -> Sequence[Device]:
    result = await session.execute(
        select(Device)
        .options(selectinload(Device.patient))
        .order_by(Device.created_at)
    )
    return result.scalars().all()


async def get_by_device_id(session: AsyncSession, device_id: str) -> Device | None:
    result = await session.execute(
        select(Device)
        .options(selectinload(Device.patient))
        .where(Device.device_id == device_id)
    )
    return result.scalar_one_or_none()


async def get_by_patient_id(session: AsyncSession, patient_id: str) -> Sequence[Device]:
    result = await session.execute(
        select(Device)
        .join(Patient)
        .options(selectinload(Device.patient))
        .where(Patient.patient_id == patient_id)
        .order_by(Device.created_at)
    )
    return result.scalars().all()
