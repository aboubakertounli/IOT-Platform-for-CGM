"""Service layer for device operations."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.repositories import device_repository as repo
from app.repositories import patient_repository as patient_repo
from app.schemas.device import DeviceResponse


def _to_response(d: Device) -> DeviceResponse:
    return DeviceResponse(
        id=d.id,
        device_id=d.device_id,
        patient_id=d.patient.patient_id,
        status=d.status,
        created_at=d.created_at,
    )


async def list_devices(session: AsyncSession) -> list[DeviceResponse]:
    devices = await repo.list_all(session)
    return [_to_response(d) for d in devices]


async def get_device(session: AsyncSession, device_id: str) -> DeviceResponse:
    device = await repo.get_by_device_id(session, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
    return _to_response(device)


async def get_devices_for_patient(session: AsyncSession, patient_id: str) -> list[DeviceResponse]:
    patient = await patient_repo.get_by_patient_id(session, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    devices = await repo.get_by_patient_id(session, patient_id)
    return [_to_response(d) for d in devices]
