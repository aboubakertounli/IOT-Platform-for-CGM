"""Ingestion service — full pipeline from validated reading to DB.

Orchestrates: upsert entities → fetch context → analyze → persist enriched
measurement → evaluate alerts → persist alerts.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.database import async_session
from app.models.glucose_measurement import GlucoseMeasurement
from app.repositories import glucose_repository as glucose_repo
from app.repositories import threshold_repository as threshold_repo
from app.schemas.glucose import GlucoseReading
from app.services.alert_service import AlertService
from app.services.glucose_analysis_service import GlucoseAnalysisService

logger = logging.getLogger(__name__)
settings = get_settings()


class IngestionService:
    """Centralized ingestion layer for validated sensor readings."""

    def __init__(self) -> None:
        self._session_factory = async_session
        self._analysis = GlucoseAnalysisService()
        self._alerts = AlertService()

    async def ingest(self, reading: GlucoseReading) -> None:
        """Full ingestion pipeline for a single reading."""
        try:
            async with self._session_factory() as session:
                async with session.begin():
                    await self._process(session, reading)
            logger.info(
                "PERSISTED | patient=%s device=%s seq=%d glucose=%.1f %s",
                reading.patient_id, reading.device_id,
                reading.sequence_number, reading.glucose_mg_dl, reading.unit,
            )
        except Exception as exc:
            logger.error(
                "PERSIST FAILED | patient=%s seq=%d: %s",
                reading.patient_id, reading.sequence_number, exc,
            )

    async def _process(self, session: AsyncSession, reading: GlucoseReading) -> None:
        # 1. Upsert patient and device
        patient_pk = await glucose_repo.ensure_patient(session, reading.patient_id)
        device_pk = await glucose_repo.ensure_device(session, reading.device_id, patient_pk)

        # 2. Fetch context for analysis
        recent = await glucose_repo.get_recent_for_analysis(
            session, patient_pk, before=reading.timestamp,
            hours=settings.ANALYSIS_ANOMALY_WINDOW_HOURS,
        )
        thresholds = await threshold_repo.get_for_patient(session, patient_pk)

        # 3. Run analysis
        analysis = self._analysis.analyze(
            reading.glucose_mg_dl, reading.timestamp, recent, thresholds,
        )

        # 4. Persist enriched measurement
        measurement = GlucoseMeasurement(
            patient_id=patient_pk,
            device_id=device_pk,
            timestamp=reading.timestamp,
            glucose_mg_dl=reading.glucose_mg_dl,
            unit=reading.unit,
            sequence_number=reading.sequence_number,
            classification=analysis.classification,
            trend_direction=analysis.trend_direction,
            trend_rate=analysis.trend_rate,
            is_anomaly=analysis.is_anomaly,
            anomaly_score=analysis.anomaly_score,
        )
        session.add(measurement)
        await session.flush()

        # 5. Evaluate and persist alerts
        await self._alerts.evaluate_and_persist(
            session, patient_pk, device_pk, measurement.id,
            reading.glucose_mg_dl, analysis, thresholds,
        )


# Module-level singleton used by handlers
ingestion_service = IngestionService()
