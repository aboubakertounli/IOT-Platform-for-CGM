"""Service layer for patient operations."""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import patient_repository as repo
from app.schemas.patient import PatientResponse


async def list_patients(session: AsyncSession) -> list[PatientResponse]:
    patients = await repo.list_all(session)
    return [PatientResponse.model_validate(p) for p in patients]


async def get_patient(session: AsyncSession, patient_id: str) -> PatientResponse:
    patient = await repo.get_by_patient_id(session, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    return PatientResponse.model_validate(patient)
