"""Read-only queries for patients."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient


async def list_all(session: AsyncSession) -> Sequence[Patient]:
    result = await session.execute(
        select(Patient).order_by(Patient.created_at)
    )
    return result.scalars().all()


async def get_by_patient_id(session: AsyncSession, patient_id: str) -> Patient | None:
    result = await session.execute(
        select(Patient).where(Patient.patient_id == patient_id)
    )
    return result.scalar_one_or_none()
