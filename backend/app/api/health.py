"""Health and debug endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.alert import Alert
from app.models.device import Device
from app.models.glucose_measurement import GlucoseMeasurement
from app.models.patient import Patient

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Basic liveness check — the backend process is up."""
    return {
        "status": "ok",
        "service": "cgm-iot-backend",
    }


@router.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db)):
    """Readiness check — the backend can reach PostgreSQL."""
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        return {
            "status": "ok",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(e),
        }


@router.get("/debug/stats")
async def debug_stats(db: AsyncSession = Depends(get_db)):
    """Quick count of persisted measurements — useful for testing the pipeline."""
    result = await db.execute(
        select(func.count()).select_from(GlucoseMeasurement)
    )
    return {"measurements_count": result.scalar_one()}


@router.get("/api/debug/summary")
async def debug_summary(db: AsyncSession = Depends(get_db)):
    """Full pipeline health summary — counts for all main entities."""
    patients = await db.execute(select(func.count()).select_from(Patient))
    devices = await db.execute(select(func.count()).select_from(Device))
    measurements = await db.execute(select(func.count()).select_from(GlucoseMeasurement))
    alerts = await db.execute(select(func.count()).select_from(Alert))
    active_alerts = await db.execute(
        select(func.count()).select_from(Alert).where(Alert.status == "active")
    )
    return {
        "patients_count": patients.scalar_one(),
        "devices_count": devices.scalar_one(),
        "measurements_count": measurements.scalar_one(),
        "alerts_count": alerts.scalar_one(),
        "active_alerts_count": active_alerts.scalar_one(),
    }
