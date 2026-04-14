"""Queries for alerts."""

from collections.abc import Sequence
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import AlertStatus
from app.models.alert import Alert


async def has_recent_similar(
    session: AsyncSession,
    patient_pk: int,
    alert_type: str,
    dedup_minutes: int,
) -> bool:
    """Check if a similar active alert already exists within the dedup window."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=dedup_minutes)
    result = await session.execute(
        select(func.count())
        .select_from(Alert)
        .where(
            Alert.patient_id == patient_pk,
            Alert.type == alert_type,
            Alert.status == AlertStatus.ACTIVE,
            Alert.created_at >= cutoff,
        )
    )
    return result.scalar_one() > 0


# ── API read queries ──────────────────────────────


async def list_all(
    session: AsyncSession,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Alert]:
    result = await session.execute(
        select(Alert)
        .options(selectinload(Alert.patient))
        .order_by(Alert.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


async def get_by_patient(
    session: AsyncSession,
    patient_pk: int,
    limit: int = 100,
) -> Sequence[Alert]:
    result = await session.execute(
        select(Alert)
        .options(selectinload(Alert.patient))
        .where(Alert.patient_id == patient_pk)
        .order_by(Alert.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def get_active_by_patient(
    session: AsyncSession,
    patient_pk: int,
) -> Sequence[Alert]:
    result = await session.execute(
        select(Alert)
        .options(selectinload(Alert.patient))
        .where(
            Alert.patient_id == patient_pk,
            Alert.status == AlertStatus.ACTIVE,
        )
        .order_by(Alert.created_at.desc())
    )
    return result.scalars().all()


async def get_by_id(session: AsyncSession, alert_id: int) -> Alert | None:
    result = await session.execute(
        select(Alert)
        .options(selectinload(Alert.patient))
        .where(Alert.id == alert_id)
    )
    return result.scalar_one_or_none()


async def acknowledge(session: AsyncSession, alert_id: int) -> Alert | None:
    """Mark an alert as acknowledged. Returns the updated alert or None."""
    alert = await get_by_id(session, alert_id)
    if alert is None:
        return None
    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_at = datetime.now(timezone.utc)
    return alert
