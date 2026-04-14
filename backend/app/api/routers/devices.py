"""Device endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.device import DeviceResponse
from app.services import device_service

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("", response_model=list[DeviceResponse])
async def list_devices(db: AsyncSession = Depends(get_db)):
    return await device_service.list_devices(db)


@router.get("/patient/{patient_id}", response_model=list[DeviceResponse])
async def get_devices_for_patient(patient_id: str, db: AsyncSession = Depends(get_db)):
    return await device_service.get_devices_for_patient(db, patient_id)


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str, db: AsyncSession = Depends(get_db)):
    return await device_service.get_device(db, device_id)
