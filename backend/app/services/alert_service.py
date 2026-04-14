"""Alert rule evaluation and persistence.

Evaluates glucose-level, trend, and anomaly rules.
Deduplicates: skips alerts of the same type if one already exists within the dedup window.
"""

import logging
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.enums import (
    AlertSeverity,
    AlertType,
    GlucoseClassification,
    TrendDirection,
)
from app.models.alert import Alert
from app.repositories import alert_repository as alert_repo
from app.repositories.threshold_repository import ThresholdValues
from app.schemas.analysis import AnalysisResult

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class AlertCandidate:
    type: AlertType
    severity: AlertSeverity
    message: str


_MESSAGES = {
    AlertType.SEVERE_HYPOGLYCEMIA: "Critical hypoglycemia: {g:.0f} mg/dL",
    AlertType.HYPOGLYCEMIA: "Low glucose: {g:.0f} mg/dL",
    AlertType.SEVERE_HYPERGLYCEMIA: "Critical hyperglycemia: {g:.0f} mg/dL",
    AlertType.HYPERGLYCEMIA: "High glucose: {g:.0f} mg/dL",
    AlertType.RAPID_RISE: "Rapidly rising glucose: {g:.0f} mg/dL ({r:+.1f} mg/dL/min)",
    AlertType.RAPID_FALL: "Rapidly falling glucose: {g:.0f} mg/dL ({r:+.1f} mg/dL/min)",
    AlertType.ANOMALY: "Anomalous glucose reading: {g:.0f} mg/dL (z-score {z:.1f})",
}


class AlertService:

    def evaluate_rules(
        self,
        glucose: float,
        analysis: AnalysisResult,
        thresholds: ThresholdValues,
    ) -> list[AlertCandidate]:
        """Pure rule evaluation — no DB access."""
        candidates: list[AlertCandidate] = []

        # Glucose-level alerts (most severe wins)
        if glucose < thresholds.hypo_critical:
            candidates.append(AlertCandidate(
                AlertType.SEVERE_HYPOGLYCEMIA, AlertSeverity.CRITICAL,
                _MESSAGES[AlertType.SEVERE_HYPOGLYCEMIA].format(g=glucose),
            ))
        elif glucose < thresholds.hypo_warning:
            candidates.append(AlertCandidate(
                AlertType.HYPOGLYCEMIA, AlertSeverity.WARNING,
                _MESSAGES[AlertType.HYPOGLYCEMIA].format(g=glucose),
            ))
        elif glucose > thresholds.hyper_critical:
            candidates.append(AlertCandidate(
                AlertType.SEVERE_HYPERGLYCEMIA, AlertSeverity.CRITICAL,
                _MESSAGES[AlertType.SEVERE_HYPERGLYCEMIA].format(g=glucose),
            ))
        elif glucose > thresholds.hyper_warning:
            candidates.append(AlertCandidate(
                AlertType.HYPERGLYCEMIA, AlertSeverity.WARNING,
                _MESSAGES[AlertType.HYPERGLYCEMIA].format(g=glucose),
            ))

        # Trend alerts (only when direction + current zone combine dangerously)
        if (
            analysis.trend_direction == TrendDirection.RAPID_RISE
            and glucose > thresholds.hyper_warning
        ):
            candidates.append(AlertCandidate(
                AlertType.RAPID_RISE, AlertSeverity.WARNING,
                _MESSAGES[AlertType.RAPID_RISE].format(g=glucose, r=analysis.trend_rate),
            ))
        elif (
            analysis.trend_direction == TrendDirection.RAPID_FALL
            and glucose < thresholds.hypo_warning
        ):
            candidates.append(AlertCandidate(
                AlertType.RAPID_FALL, AlertSeverity.WARNING,
                _MESSAGES[AlertType.RAPID_FALL].format(g=glucose, r=analysis.trend_rate),
            ))

        # Anomaly alert
        if analysis.is_anomaly:
            candidates.append(AlertCandidate(
                AlertType.ANOMALY, AlertSeverity.INFO,
                _MESSAGES[AlertType.ANOMALY].format(g=glucose, z=analysis.anomaly_score),
            ))

        return candidates

    async def evaluate_and_persist(
        self,
        session: AsyncSession,
        patient_pk: int,
        device_pk: int,
        measurement_id: int,
        glucose: float,
        analysis: AnalysisResult,
        thresholds: ThresholdValues,
    ) -> int:
        """Evaluate rules, deduplicate, persist. Returns count of alerts created."""
        candidates = self.evaluate_rules(glucose, analysis, thresholds)
        created = 0

        for c in candidates:
            if await alert_repo.has_recent_similar(
                session, patient_pk, c.type, settings.ALERT_DEDUP_MINUTES,
            ):
                continue

            session.add(Alert(
                patient_id=patient_pk,
                device_id=device_pk,
                measurement_id=measurement_id,
                type=c.type,
                severity=c.severity,
                message=c.message,
            ))
            created += 1
            logger.info(
                "ALERT | patient_pk=%d type=%s severity=%s: %s",
                patient_pk, c.type, c.severity, c.message,
            )

        return created
