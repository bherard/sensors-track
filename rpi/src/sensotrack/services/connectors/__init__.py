# -*- coding: utf-8 -*-
"""Connectors service."""
import importlib
import logging
import threading
import time
from typing import Any

from sensotrack.services.bus import MQTTClient

class CommandReceiver(MQTTClient):
    """MQTT receiver for command comming from core PF to sensors"""

    def __init__(self, conf, supported_sensors, on_command, pool=10) -> None:
        self._supported_sensors = supported_sensors
        self._on_command = on_command
        super().__init__(conf, ["sensors/command/#"], pool)

    def process_message(self, msg):
        """Process messages comming from core PF (commands)

        :param msg: message to process
        :type msg: MQTTMessage
        """

        sensor_id = msg.topic.split("/")[-1]
        if sensor_id in self._supported_sensors():
            self._on_command(sensor_id, msg.payload.decode("utf8")) #pylint: disable=not-callable

class Connector:
    """Connector abstract class."""

    def __init__(self, conf):
        self._conf = conf
        self._logger = logging.getLogger(__name__)
        self._command_receiver = CommandReceiver(
            self._conf,
            self.supported_sensors,
            self.on_command
        )
        self._running = False
        self._main_thread = None

    def on_start(self):
        """Method called when connector start."""

    def _start_impl(self):
        self._logger.info("Starting connector %s", __name__)
        self._running = True
        self.on_start()
        while self._running:
            data = self.read_data()
            if data:
                self._command_receiver.publish(
                    f'sensors/data/{data["sid"]}',
                    data["data"]
                )

            time.sleep(0.01)



    def supported_sensors(self):
        """Abstract method returning a list of supported sensors ID."""
        raise NotImplementedError()
        #return list[str]

    def on_command(self, sid, command):
        """Abstract command call to process a command comming from core PF

        :param sid: target sensor identifier
        :type sid: str
        :param command: command to apply to sebnsor
        :type command: str
        """
        raise NotImplementedError()

    def read_data(self):
        """Read data from a sensor and return it with the followinf dict:
        {
            "sid": "sensor_id",
            "data": "some-data"
        }


        :return: Data if any
        :rtype: dict|Nobne
        """
        raise NotImplementedError()
        # return {
        #     "sid": "sensor_id",
        #     "data": "some-data"
        # }

    def start(self):
        """Start the connector."""

        self._command_receiver.start()

        self._main_thread = threading.Thread(
            target=self._start_impl,
            daemon=True
        )
        self._main_thread.start()

    def stop(self):
        """Stop main loop"""
        self._running = False
        self._command_receiver.stop()

    def join(self):
        """Wait until connector stops."""
        if self._main_thread:
            self._main_thread.join()
        self._command_receiver.join()


class ConnectorsManager:
    """Connectors manager implem."""
    _connectors = []

    def __init__(self, conf) -> None:
        self._conf = conf
        self._logger = logging.getLogger(__name__)

    def _get_class(self, name):
        components = name.split('.')
        mod_name = ".".join(components[:-1])
        class_name = components[-1]
        try:
            mod = importlib.import_module(mod_name)
            return getattr(mod, class_name)
        except ModuleNotFoundError:
            return None
        except AttributeError:
            self._logger.error(
                "Class %s not foun,d in %s",
                class_name,
                mod_name
            )
            raise

    @property
    def connectors(self):
        """Get list of started connectors."""
        return self._connectors

    def start_connectors(self):
        """Start connector defnied in configuration."""
        self._update_logging_level()
        for conn in self._conf["connectors"]:
            self._logger.debug("Found connector %s in configuration", conn["class"])
            klass = self._get_class(conn["class"])
            if klass:
                connector = klass(self._conf)
                self._connectors.append(connector)
                connector.start()
            else:
                self._logger.error("No module found for %s", conn["class"])

    def _update_logging_level(self):
        """Update connector config according to configuration."""
        for conn in self._conf["connectors"]:
            class_name = conn["class"]
            components = class_name.split('.')
            mod_name = ".".join(components[:-1])
            logging.getLogger(mod_name).setLevel(
                logging.getLevelName(
                    conn["logLevel"].upper()
                )
            )
