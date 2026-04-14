from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("devices.id"), default=None)
    measurement_id: Mapped[int | None] = mapped_column(
        ForeignKey("glucose_measurements.id"), default=None,
    )
    type: Mapped[str] = mapped_column(String(50), index=True)
    severity: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), index=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(default=None)
    resolved_at: Mapped[datetime | None] = mapped_column(default=None)

    patient: Mapped["Patient"] = relationship()

    def __repr__(self) -> str:
        return f"<Alert {self.type} {self.severity} patient={self.patient_id}>"
