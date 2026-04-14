"""Pure computation service for glucose analysis.

No database access — receives data, returns results.
Three analysis blocks:
  A. Classification (threshold-based)
  B. Trend detection (linear regression on recent window)
  C. Anomaly detection (z-score against 24h baseline)
"""

import statistics
from collections.abc import Sequence
from datetime import datetime, timedelta

from app.core.config import get_settings
from app.core.enums import GlucoseClassification, TrendDirection
from app.models.glucose_measurement import GlucoseMeasurement
from app.repositories.threshold_repository import ThresholdValues
from app.schemas.analysis import AnalysisResult

settings = get_settings()


class GlucoseAnalysisService:

    def __init__(self) -> None:
        self._trend_window = settings.ANALYSIS_TREND_WINDOW_MINUTES
        self._trend_min = settings.ANALYSIS_TREND_MIN_POINTS
        self._anomaly_z = settings.ANALYSIS_ANOMALY_Z_THRESHOLD
        self._anomaly_min = settings.ANALYSIS_ANOMALY_MIN_POINTS

    def analyze(
        self,
        glucose: float,
        timestamp: datetime,
        recent: Sequence[GlucoseMeasurement],
        thresholds: ThresholdValues,
    ) -> AnalysisResult:
        classification = self._classify(glucose, thresholds)
        trend_dir, trend_rate = self._compute_trend(glucose, timestamp, recent)
        is_anomaly, anomaly_score = self._detect_anomaly(glucose, recent)
        return AnalysisResult(
            classification=classification,
            trend_direction=trend_dir,
            trend_rate=trend_rate,
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
        )

    # ── A. Classification ─────────────────────────

    def _classify(
        self, glucose: float, t: ThresholdValues,
    ) -> GlucoseClassification:
        if glucose < t.hypo_critical or glucose > t.hyper_critical:
            return GlucoseClassification.CRITICAL
        if glucose < t.hypo_warning or glucose > t.hyper_warning:
            return GlucoseClassification.WARNING
        return GlucoseClassification.NORMAL

    # ── B. Trend detection ────────────────────────

    def _compute_trend(
        self,
        current_glucose: float,
        current_ts: datetime,
        recent: Sequence[GlucoseMeasurement],
    ) -> tuple[TrendDirection, float]:
        """Linear regression over the recent window + current point.

        Returns (direction, slope in mg/dL per minute).
        """
        cutoff = current_ts - timedelta(minutes=self._trend_window)
        window: list[tuple[datetime, float]] = [
            (m.timestamp, m.glucose_mg_dl) for m in recent if m.timestamp >= cutoff
        ]
        window.append((current_ts, current_glucose))

        if len(window) < self._trend_min:
            return TrendDirection.STABLE, 0.0

        t0 = window[0][0]
        xs = [(ts - t0).total_seconds() / 60.0 for ts, _ in window]
        ys = [v for _, v in window]

        slope = self._least_squares_slope(xs, ys)
        direction = self._slope_to_direction(slope)
        return direction, round(slope, 3)

    @staticmethod
    def _least_squares_slope(xs: list[float], ys: list[float]) -> float:
        n = len(xs)
        sum_x = sum(xs)
        sum_y = sum(ys)
        sum_xy = sum(x * y for x, y in zip(xs, ys))
        sum_x2 = sum(x * x for x in xs)
        denom = n * sum_x2 - sum_x * sum_x
        if denom == 0:
            return 0.0
        return (n * sum_xy - sum_x * sum_y) / denom

    @staticmethod
    def _slope_to_direction(slope: float) -> TrendDirection:
        if slope > 3.0:
            return TrendDirection.RAPID_RISE
        if slope > 1.0:
            return TrendDirection.RISING
        if slope < -3.0:
            return TrendDirection.RAPID_FALL
        if slope < -1.0:
            return TrendDirection.FALLING
        return TrendDirection.STABLE

    # ── C. Anomaly detection ──────────────────────

    def _detect_anomaly(
        self,
        current_glucose: float,
        recent: Sequence[GlucoseMeasurement],
    ) -> tuple[bool, float]:
        """Z-score of the current reading against the historical baseline."""
        if len(recent) < self._anomaly_min:
            return False, 0.0

        values = [m.glucose_mg_dl for m in recent]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)

        if stdev < 1.0:
            return False, 0.0

        z = abs(current_glucose - mean) / stdev
        return z > self._anomaly_z, round(z, 2)
