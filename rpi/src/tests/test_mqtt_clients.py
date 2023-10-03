import datetime
import logging
import time
import unittest

import mock
import paho.mqtt.client as mqtt
from paho.mqtt.properties import Properties as Properties
from sensotrack.services.bus import Receiver

from sensotrack.services.connectors import MQTTClient

class BasicMQTTClient(MQTTClient):
    """Basic implementation for testing."""

    last_message = None

    def process_message(self, msg):
        self.last_message = msg



class MockMqttClient(mqtt.Client):
    '''Mock imple form paho mqtt Client.'''

    count = 0
    def connect(self, host: str, port: int = 1883, keepalive: int = 60, bind_address: str = "", bind_port: int = 0, clean_start: int = 3, properties: Properties | None = None) -> int:
        """Simulate connection issues."""
        if self.count > 1:
            return super().connect(host, port, keepalive, bind_address, bind_port, clean_start, properties)
        else:
            self.count += 1
            raise ConnectionRefusedError()

class TestMqttClientAbstract(unittest.TestCase):
    """Test common errors return codes."""


    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG)

    def test_start_stop(self):
        """Test Start and stop."""

        conf = {
            "mqtt": {
                "host": "localhost",
                "port": 1883
            }
        }

        client = BasicMQTTClient(conf, ["foo/bar"])
        client.start()
        time.sleep(0.1)
        client.stop()
        client.join()

    def test_publish_receive(self):
        """Test Start and stop."""

        conf = {
            "mqtt": {
                "host": "localhost",
                "port": 1883
            }
        }

        client = BasicMQTTClient(conf, ["foo/bar/#"])
        client.start()
        time.sleep(0.1)
        client.publish("foo/bar", "data")
        time.sleep(0.1)
        client.stop()
        client.join()

        self.assertEqual(client.last_message.topic, "foo/bar")
        self.assertEqual(client.last_message.payload, b"data")

    @mock.patch("paho.mqtt.client.Client")
    def test_retry_connection(self, mqtt_mock):
        """Test Start and stop."""

        conf = {
            "mqtt": {
                "host": "localhost",
                "port": 1883
            }
        }

        mqtt_mock.return_value = MockMqttClient()

        client = BasicMQTTClient(conf, ["foo/bar"])
        client.WAIT_BEFORE_RETRY = 0.1
        client.start()
        time.sleep(0.1)
        client.stop()
        client.join()

        self.assertGreater(mqtt_mock.return_value.count, 0)

class TestsBusReceiver(unittest.TestCase):
    """Test MQTT Bus data receiver."""

    @mock.patch(
        "sensotrack.dao.SensorDAO.upsert"
    )
    def test_recieve_data(self, dao_mock):
        '''Test sensor data reception form bus.'''

        conf = {
            "mqtt": {
                "host": "localhost",
                "port": 1883
            }
        }

        msg = mock.MagicMock()
        msg.topic = "sensors/data/random-sensor"
        msg.payload = b'random-payload'

        reciever =  Receiver(conf)
        reciever.process_message(msg)
        self.assertTrue(dao_mock.called)

        stored_data = dao_mock.call_args[0][0]
        self.assertEqual(stored_data["sensorId"], "random-sensor")
        self.assertEqual(stored_data["value"], "random-payload")
        datetime.datetime.fromisoformat(stored_data["measurementDate"])
