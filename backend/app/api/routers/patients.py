"""Patient endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.patient import PatientResponse
from app.services import patient_service

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.get("", response_model=list[PatientResponse])
async def list_patients(db: AsyncSession = Depends(get_db)):
    return await patient_service.list_patients(db)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str, db: AsyncSession = Depends(get_db)):
    return await patient_service.get_patient(db, patient_id)
