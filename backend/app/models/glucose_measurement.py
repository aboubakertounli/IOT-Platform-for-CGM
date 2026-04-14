from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base


class GlucoseMeasurement(Base):
    __tablename__ = "glucose_measurements"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(index=True)
    glucose_mg_dl: Mapped[float]
    unit: Mapped[str] = mapped_column(String(10), default="mg/dL")
    sequence_number: Mapped[int]

    # Analysis fields (populated by GlucoseAnalysisService)
    classification: Mapped[str | None] = mapped_column(String(20), default=None)
    trend_direction: Mapped[str | None] = mapped_column(String(20), default=None)
    trend_rate: Mapped[float | None] = mapped_column(default=None)
    is_anomaly: Mapped[bool | None] = mapped_column(default=None)
    anomaly_score: Mapped[float | None] = mapped_column(default=None)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    patient: Mapped["Patient"] = relationship(back_populates="measurements")
    device: Mapped["Device"] = relationship(back_populates="measurements")

    def __repr__(self) -> str:
        return f"<GlucoseMeasurement patient={self.patient_id} seq={self.sequence_number}>"
