import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass
class PatientConfig:
    patient_id: str
    device_id: str
    csv_path: str


@dataclass
class Config:
    # MQTT
    mqtt_broker_host: str = os.getenv("MQTT_BROKER_HOST", "localhost")
    mqtt_broker_port: int = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    mqtt_qos: int = int(os.getenv("MQTT_QOS", "1"))

    # Simulation
    interval_seconds: float = float(os.getenv("EDGE_INTERVAL_SECONDS", "5"))

    # CSV column mapping — adapt these if your dataset uses different names
    col_timestamp: str = os.getenv("COL_TIMESTAMP", "timestamp")
    col_glucose: str = os.getenv("COL_GLUCOSE", "glucose")

    # Patients — built from environment or defaults
    patients: list[PatientConfig] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.patients:
            return
        self._load_patients_from_env()

    def _load_patients_from_env(self) -> None:
        """Load patient definitions from EDGE_PATIENTS_* env vars.

        Expected format (1-indexed):
            EDGE_PATIENTS_1_ID=PAT-001
            EDGE_PATIENTS_1_DEVICE=DEX-G6-001
            EDGE_PATIENTS_1_CSV=data/patient_001.csv

        Falls back to a single default patient if nothing is set.
        """
        index = 1
        while True:
            pid = os.getenv(f"EDGE_PATIENTS_{index}_ID")
            if pid is None:
                break
            device = os.getenv(f"EDGE_PATIENTS_{index}_DEVICE", f"DEX-G6-{index:03d}")
            csv_path = os.getenv(f"EDGE_PATIENTS_{index}_CSV", f"data/patient_{index:03d}.csv")
            self.patients.append(PatientConfig(patient_id=pid, device_id=device, csv_path=csv_path))
            index += 1

        if not self.patients:
            self.patients.append(
                PatientConfig(
                    patient_id=os.getenv("EDGE_PATIENT_ID", "PAT-001"),
                    device_id=os.getenv("EDGE_DEVICE_ID", "DEX-G6-001"),
                    csv_path=os.getenv("EDGE_CSV_PATH", "data/sample.csv"),
                )
            )
