"""Domain enums used across the CGM platform."""

from enum import StrEnum


class GlucoseClassification(StrEnum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


class TrendDirection(StrEnum):
    RAPID_RISE = "rapid_rise"
    RISING = "rising"
    STABLE = "stable"
    FALLING = "falling"
    RAPID_FALL = "rapid_fall"


class AlertType(StrEnum):
    SEVERE_HYPOGLYCEMIA = "severe_hypoglycemia"
    HYPOGLYCEMIA = "hypoglycemia"
    HYPERGLYCEMIA = "hyperglycemia"
    SEVERE_HYPERGLYCEMIA = "severe_hyperglycemia"
    RAPID_RISE = "rapid_rise"
    RAPID_FALL = "rapid_fall"
    ANOMALY = "anomaly"


class AlertSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(StrEnum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
