
import logging
import time
import unittest

import mock
import paho.mqtt.client as mqtt

from sensotrack.services.connectors import ConnectorsManager, Connector

class ConnectorBasicImpl(Connector):
    """Basic implementation for testing."""
    last_command = None
    read_count = 0

    def on_command(self, sid, command):
        self.last_command = {
            "sid": sid,
            "command": command
        }

    def read_data(self):
        if self.read_count == 0:
            ret = {
                "sid": "A",
                "data": "my-data"
            }
        else:
            ret = None

        self.read_count +=1
        return ret
    
    def supported_sensors(self):
        return ["A", "B", "C"]
    
class TestConnectorAbstract(unittest.TestCase):
    """Test Absctract connector."""

    def test_start_stop(self):
        """Test start and stop."""

        conf = {
            "mqtt": {
                "host": "localhost",
                "port": 1883
            }
        }
        connector = ConnectorBasicImpl(conf)
        connector.start()
        time.sleep(0.1)
        connector.stop()
        connector.join()

    def test_receive_command(self):
        '''Test command reception from core PF.'''

        conf = {
            "mqtt": {
                "host": "localhost",
                "port": 1883
            }
        }
        connector = ConnectorBasicImpl(conf)
        connector.start()
        time.sleep(0.1)

        mqtt_client = mqtt.Client(__name__, True)
        mqtt_client.connect(
            conf["mqtt"]["host"], conf["mqtt"]["port"]
        )
        mqtt_client.publish("sensors/command/A", "my-command")
        time.sleep(0.5)

        connector.stop()
        connector.join()

        self.assertEqual(connector.last_command["sid"], "A")
        self.assertEqual(connector.last_command["command"], "my-command")


    @mock.patch("sensotrack.services.connectors.CommandReceiver.publish")
    def test_data_reception(self, publish_mock):
        """Test data reception form sensor."""

        conf = {
            "mqtt": {
                "host": "localhost",
                "port": 1883
            }
        }
        connector = ConnectorBasicImpl(conf)
        connector.start()
        time.sleep(0.1)
        connector.stop()
        connector.join()
        self.assertEqual(publish_mock.call_args[0][0], 'sensors/data/A')
        self.assertEqual(publish_mock.call_args[0][1], 'my-data')


class TestsConnectorsManager(unittest.TestCase):
    """Test CommenctorManager."""

    class ConnectorMock():
        """Connector Mock implementation."""

        def __init__(self, conf) -> None:
            self.start_called = False
            self.conf = conf

        def start(self):
            """Mock start."""
            self.start_called=True

    @mock.patch(
        "sensotrack.services.connectors.ConnectorsManager._get_class",
        mock.MagicMock(return_value=ConnectorMock)
    )
    def test_start_connector(self):
        """Test if constructor are created and started."""

        conf ={
            "connectors": [
                {
                    "class": "sensotrack.services.connectors.foo.Bar",
                    "logLevel": "DEBUG"
                },
                {
                    "class": "sensotrack.services.connectors.ispum.Lorem",
                    "logLevel": "DEBUG"
                }
            ]
        }
        manager = ConnectorsManager(
            conf
        )
        manager.start_connectors()

        # ensure connectors are started
        self.assertEqual(len(conf["connectors"]), len(manager.connectors))
        for connector in manager.connectors:
            self.assertTrue(connector.start_called)
            self.assertEqual(connector.conf, conf)

        # Ensure proper log level is set to connectors
        for conn in conf["connectors"]:
            class_name = conn["class"]
            components = class_name.split('.')
            mod_name = ".".join(components[:-1])
            self.assertEqual(
                logging.getLogger(mod_name).level,
                logging.getLevelName(
                    conn["logLevel"].upper()
                )
            )
