from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    first_name: Mapped[str | None] = mapped_column(String(100), default=None)
    last_name: Mapped[str | None] = mapped_column(String(100), default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    devices: Mapped[list["Device"]] = relationship(back_populates="patient")
    measurements: Mapped[list["GlucoseMeasurement"]] = relationship(back_populates="patient")

    def __repr__(self) -> str:
        return f"<Patient {self.patient_id}>"
