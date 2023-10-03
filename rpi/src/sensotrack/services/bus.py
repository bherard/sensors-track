# -*- coding: utf-8 -*-
"""Asynch bus service."""
import logging
from threading import Thread, BoundedSemaphore
import time

import paho.mqtt.client as mqtt

from sensotrack.services.sensors import SensorService
from sensotrack.utils.exceptions import STException

class MQTTClient:
    """Async MQTT bus receiver."""
    WAIT_BEFORE_RETRY = 1
    def __init__(self, conf, topics=None, pool=10) -> None:
        self._conf = conf
        self._logger = logging.getLogger(__name__)
        self._sem = BoundedSemaphore(pool)
        self._mqtt_client = None
        if topics:
            self._topics = topics
        else:
            raise STException(
                "Subscription topics list can't be empty",
                400
            )
        self._running = False
        self._main_thread = None


    # Method tigggerd by MQTT client on connection to MQTT Server
    def _on_connect(self, client, userdata, flags, return_code):
        """Subscribe to MQTT topic when connected."""

        self._logger.info("Connected to MQTT server with result code %s: ", return_code)
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # Subscribe to publishing Queue

        self._logger.info("Subscribing to topics %s", self._topics)
        client.subscribe([(topic ,0) for topic in self._topics])

    def _on_message(self, client, userdata, msg):
        """Receive message form MQTT and process it as // thread."""

        self._sem.acquire()
        Thread(target=self._process_message, args=(msg,)).start()

    def _process_message(self, msg):

        self.process_message(msg)
        self._sem.release()

    def process_message(self, msg):
        """Process a message."""

        raise NotImplementedError()

    def _on_disconnect(self, client, userdata, rc):
        self._logger.debug("Disconnected")
        client.loop_stop(True)
        client.disconnect()

    def _start_implem(self):
        self._mqtt_client = mqtt.Client(
            "mqttListener." + str(time.time()),
            False
        )
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_message = self._on_message
        self._mqtt_client.on_disconnect = self._on_disconnect

        self._running = True
        self._logger.info("Connecting to MQTT bus at %s", self._conf["mqtt"]["host"])
        while not self._mqtt_client.is_connected() and self._running:
            try:
                self._mqtt_client.connect(
                    self._conf["mqtt"]["host"],
                    self._conf["mqtt"]["port"],
                    60
                )
                self._mqtt_client.loop_forever()
            except ConnectionRefusedError:
                self._logger.warning(
                    "Can't connect to MQTT bus as %s",
                    self._conf["mqtt"]["host"]
                )
                time.sleep(self.WAIT_BEFORE_RETRY)
        self._running = False

    def publish(self, topic, message):
        """Publish a message to MQTT."""
        if self._mqtt_client and self._mqtt_client.is_connected():
            self._mqtt_client.publish(topic, message)

    def start(self):
        """Starts bus messages reviever."""

        self._main_thread = Thread(
            target=self._start_implem,
            daemon=True
        )
        self._main_thread.start()

    def join(self):
        """Wait for main thread end."""
        if self._main_thread:
            self._main_thread.join()

    def stop(self):
        """Stop main thread."""
        self._running = False
        if self._mqtt_client and self._mqtt_client.is_connected():
            self._mqtt_client.disconnect()

class Receiver(MQTTClient):
    """Sensors data receiver."""

    def __init__(self, conf, pool=10) -> None:
        super().__init__(conf, ["sensors/data/#"], pool)
        self._sensor_svc = SensorService(conf)

    def process_message(self, msg):
        """Process data received from sensors."""

        self._logger.info("Got message from topic %s", msg.topic)
        if msg.topic.startswith("sensors/data"):
            sensor_id = msg.topic.split("/")[-1]
            value = msg.payload.decode("utf8")
            self._sensor_svc.register_new_value(sensor_id, value)
            self._logger.debug(
                "Received message %s from topic %s",
                msg.payload.decode("utf8"),
                msg.topic
            )
        else:
            self._logger.warning(
                "Ununderstood message %s from topic %s",
                msg.payload.decode("utf8"),
                msg.topic
            )
