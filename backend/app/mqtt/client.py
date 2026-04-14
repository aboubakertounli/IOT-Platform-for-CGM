"""MQTT consumer — connects to Mosquitto, subscribes, and dispatches messages."""

import logging
import time

import paho.mqtt.client as mqtt

from app.mqtt.handlers import dispatch
from app.mqtt.topics import ALL_SUBSCRIPTIONS

logger = logging.getLogger(__name__)


class MqttConsumer:
    """Background MQTT consumer integrated with FastAPI lifespan."""

    def __init__(
        self,
        host: str,
        port: int,
        qos: int = 1,
        client_id: str = "cgm-backend",
        keepalive: int = 60,
    ) -> None:
        self._host = host
        self._port = port
        self._qos = qos
        self._keepalive = keepalive
        self._connected = False

        self._client = mqtt.Client(
            client_id=client_id,
            protocol=mqtt.MQTTv311,
        )
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

    # ── Lifecycle ─────────────────────────────────────

    def start(self) -> None:
        """Connect to the broker and start the network loop in a background thread."""
        logger.info("Connecting to MQTT broker %s:%d …", self._host, self._port)
        self._client.connect(self._host, self._port, keepalive=self._keepalive)
        self._client.loop_start()

        deadline = time.time() + 10
        while not self._connected and time.time() < deadline:
            time.sleep(0.1)

        if not self._connected:
            self._client.loop_stop()
            raise ConnectionError(
                f"MQTT consumer failed to connect to {self._host}:{self._port}"
            )

    def stop(self) -> None:
        """Disconnect and stop the background network loop."""
        self._client.loop_stop()
        self._client.disconnect()
        logger.info("MQTT consumer stopped")

    # ── Callbacks ─────────────────────────────────────

    def _on_connect(self, client: mqtt.Client, userdata: object, flags: dict, rc: int) -> None:
        if rc != 0:
            logger.error("MQTT connection refused (rc=%d)", rc)
            return

        self._connected = True
        logger.info("Connected to MQTT broker")

        for topic in ALL_SUBSCRIPTIONS:
            client.subscribe(topic, qos=self._qos)
            logger.info("Subscribed to %s (QoS %d)", topic, self._qos)

    def _on_disconnect(self, client: mqtt.Client, userdata: object, rc: int) -> None:
        self._connected = False
        if rc == 0:
            logger.info("MQTT disconnected cleanly")
        else:
            logger.warning("MQTT unexpected disconnect (rc=%d) — paho will auto-reconnect", rc)

    def _on_message(self, client: mqtt.Client, userdata: object, msg: mqtt.MQTTMessage) -> None:
        dispatch(msg.topic, msg.payload)
