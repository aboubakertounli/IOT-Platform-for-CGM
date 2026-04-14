"""Ingestion service — receives validated readings and processes them.

This is the internal entry point between MQTT ingestion and future persistence.
Phase 3: log only. Phase 4 will add database writes here.
"""

import logging

from app.schemas.glucose import GlucoseReading

logger = logging.getLogger(__name__)


class IngestionService:
    """Centralized ingestion layer for validated sensor readings."""

    def ingest(self, reading: GlucoseReading) -> None:
        """Process a validated glucose reading.

        Currently logs the reading. The next phase will persist to PostgreSQL.
        """
        logger.info(
            "INGESTED | patient=%s device=%s seq=%d glucose=%.1f %s ts=%s",
            reading.patient_id,
            reading.device_id,
            reading.sequence_number,
            reading.glucose_mg_dl,
            reading.unit,
            reading.timestamp.isoformat(),
        )
        # Phase 4: await self._persist(reading)


# Module-level singleton used by handlers
ingestion_service = IngestionService()
