import json
import logging
import time

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

TOPIC_PREFIX = "cgm/glucose"


class MqttPublisher:
    """Manages a single MQTT connection used by all patient simulators."""

    def __init__(self, host: str, port: int, qos: int = 1) -> None:
        self._host = host
        self._port = port
        self._qos = qos
        self._client = mqtt.Client(
            client_id=f"edge-sim-{int(time.time())}",
            protocol=mqtt.MQTTv311,
        )
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._connected = False

    def connect(self) -> None:
        logger.info("Connecting to MQTT broker %s:%d …", self._host, self._port)
        self._client.connect(self._host, self._port, keepalive=60)
        self._client.loop_start()
        # Wait briefly for the connection callback
        deadline = time.time() + 10
        while not self._connected and time.time() < deadline:
            time.sleep(0.1)
        if not self._connected:
            raise ConnectionError(f"Failed to connect to MQTT broker at {self._host}:{self._port}")

    def publish(self, patient_id: str, payload: dict) -> None:
        topic = f"{TOPIC_PREFIX}/{patient_id}"
        message = json.dumps(payload, default=str)
        result = self._client.publish(topic, message, qos=self._qos)
        result.wait_for_publish()
        logger.info("[%s] Published seq=%s glucose=%.1f mg/dL",
                     patient_id, payload.get("sequence_number"), payload.get("glucose_mg_dl", 0))

    def disconnect(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()
        logger.info("Disconnected from MQTT broker")

    def _on_connect(self, client: mqtt.Client, userdata: object, flags: dict, rc: int) -> None:
        if rc == 0:
            self._connected = True
            logger.info("Connected to MQTT broker")
        else:
            logger.error("MQTT connection failed with code %d", rc)

    def _on_disconnect(self, client: mqtt.Client, userdata: object, rc: int) -> None:
        self._connected = False
        if rc != 0:
            logger.warning("Unexpected MQTT disconnect (rc=%d)", rc)
