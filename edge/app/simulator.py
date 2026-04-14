import logging
import threading
import time
from datetime import datetime, timezone

from .models import GlucoseReading
from .mqtt_publisher import MqttPublisher

logger = logging.getLogger(__name__)


class PatientSimulator:
    """Replays a patient's glucose readings at a fixed interval."""

    def __init__(
        self,
        patient_id: str,
        device_id: str,
        readings: list[dict],
        publisher: MqttPublisher,
        interval_seconds: float,
    ) -> None:
        self._patient_id = patient_id
        self._device_id = device_id
        self._readings = readings
        self._publisher = publisher
        self._interval = interval_seconds
        self._stop_event = threading.Event()

    def run(self) -> None:
        total = len(self._readings)
        logger.info(
            "Starting simulation for %s (%s) — %d readings, interval=%.1fs",
            self._patient_id, self._device_id, total, self._interval,
        )

        for seq, raw in enumerate(self._readings, start=1):
            if self._stop_event.is_set():
                logger.info("Simulation stopped for %s", self._patient_id)
                return

            reading = GlucoseReading(
                device_id=self._device_id,
                patient_id=self._patient_id,
                timestamp=datetime.now(timezone.utc),
                glucose_mg_dl=raw["glucose_mg_dl"],
                sequence_number=seq,
            )

            self._publisher.publish(self._patient_id, reading.model_dump(mode="json"))

            if seq < total:
                self._stop_event.wait(timeout=self._interval)

        logger.info("Simulation complete for %s — %d readings sent", self._patient_id, total)

    def stop(self) -> None:
        self._stop_event.set()


def run_simulations(
    simulators: list[PatientSimulator],
) -> list[threading.Thread]:
    """Start each patient simulator in its own thread. Returns the thread list."""
    threads: list[threading.Thread] = []

    for sim in simulators:
        t = threading.Thread(target=sim.run, name=f"sim-{sim._patient_id}", daemon=True)
        t.start()
        threads.append(t)

    return threads
