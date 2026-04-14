"""Ingestion service — validates and persists sensor readings.

Sits between the MQTT handler layer and the repository layer.
"""

import logging

from app.db.database import async_session
from app.repositories.glucose_repository import GlucoseRepository
from app.schemas.glucose import GlucoseReading

logger = logging.getLogger(__name__)


class IngestionService:
    """Centralized ingestion layer for validated sensor readings."""

    def __init__(self) -> None:
        self._repository = GlucoseRepository(async_session)

    async def ingest(self, reading: GlucoseReading) -> None:
        """Persist a validated glucose reading to the database."""
        try:
            await self._repository.save_reading(reading)
            logger.info(
                "PERSISTED | patient=%s device=%s seq=%d glucose=%.1f %s ts=%s",
                reading.patient_id,
                reading.device_id,
                reading.sequence_number,
                reading.glucose_mg_dl,
                reading.unit,
                reading.timestamp.isoformat(),
            )
        except Exception as exc:
            logger.error(
                "PERSIST FAILED | patient=%s seq=%d: %s",
                reading.patient_id,
                reading.sequence_number,
                exc,
            )


# Module-level singleton used by handlers
ingestion_service = IngestionService()
