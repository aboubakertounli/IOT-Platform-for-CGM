import logging
import signal
import sys

from .config import Config
from .dataset_loader import load_dataset
from .mqtt_publisher import MqttPublisher
from .simulator import PatientSimulator, run_simulations

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("edge")


def main() -> None:
    config = Config()

    logger.info("=== CGM Edge Simulator ===")
    logger.info("Broker: %s:%d  |  Interval: %.1fs  |  Patients: %d",
                config.mqtt_broker_host, config.mqtt_broker_port,
                config.interval_seconds, len(config.patients))

    # Load datasets
    simulators: list[PatientSimulator] = []
    publisher = MqttPublisher(config.mqtt_broker_host, config.mqtt_broker_port, config.mqtt_qos)
    publisher.connect()

    for p in config.patients:
        logger.info("Loading dataset for %s from %s", p.patient_id, p.csv_path)
        readings = load_dataset(p.csv_path, config.col_timestamp, config.col_glucose)
        if not readings:
            logger.warning("No valid readings for %s — skipping", p.patient_id)
            continue
        simulators.append(
            PatientSimulator(p.patient_id, p.device_id, readings, publisher, config.interval_seconds)
        )

    if not simulators:
        logger.error("No patients to simulate. Check CSV paths and column names.")
        publisher.disconnect()
        sys.exit(1)

    # Graceful shutdown
    def shutdown(sig: int, frame: object) -> None:
        logger.info("Shutting down (signal %d)…", sig)
        for sim in simulators:
            sim.stop()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Run
    threads = run_simulations(simulators)
    for t in threads:
        t.join()

    publisher.disconnect()
    logger.info("=== Simulation finished ===")


if __name__ == "__main__":
    main()
