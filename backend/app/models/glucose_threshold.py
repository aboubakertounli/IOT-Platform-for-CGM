from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class GlucoseThreshold(Base):
    __tablename__ = "glucose_thresholds"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), unique=True, index=True)
    hypo_critical_mg_dl: Mapped[float] = mapped_column(default=54.0)
    hypo_warning_mg_dl: Mapped[float] = mapped_column(default=70.0)
    hyper_warning_mg_dl: Mapped[float] = mapped_column(default=180.0)
    hyper_critical_mg_dl: Mapped[float] = mapped_column(default=250.0)
    trend_rate_warning: Mapped[float] = mapped_column(default=3.0)

    patient: Mapped["Patient"] = relationship()

    def __repr__(self) -> str:
        return f"<GlucoseThreshold patient={self.patient_id}>"
