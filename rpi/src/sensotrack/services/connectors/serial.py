# -*- coding: utf-8 -*-
"""Serial (tty) connector."""
import logging
import threading
import time
import pyudev
import serial
from sensotrack.services.connectors import Connector

class TTYConnector(Connector):
    SEPARATOR = "/:/"

    _devices = {}

    def __init__(self, conf):
        super().__init__(conf)
        self._logger = logging.getLogger(__name__)

    def _get_serial(self, sid):
        for dev in self._devices.items():
            if sid in dev[1]["sensors"]:
                return dev[1]["serial"]
        return None

    def _read_line(self, ser):
        try_count = 0
        while not ser.in_waiting and try_count < 10:
            try_count += 1
            time.sleep(0.1)

        if not ser.in_waiting:
            return None
        line =  ser.readline().decode("utf-8").replace(
            "\n", ""
        ).replace(
            "\r", ""
        )
        self._logger.debug("Receive RAW data form arduino: %s", line)
        return line


    def _register_device(self, dev_name):
        MAX_TRY = 10
        try:
            self._logger.info("Registring device %s", dev_name)
            ser = serial.Serial(
                    dev_name,
                    9600,
                    timeout=0.1
                )
            time.sleep(5)
            sensors = []
            ser.write(
                f'COMMAND{TTYConnector.SEPARATOR}SENSORS\n'.encode("utf-8")
            )

            count = 0
            line = self._read_line(ser)
            while line != "***START***" and count < MAX_TRY:
                line = self._read_line(ser)
                count += 1

            if count >= MAX_TRY:
                self._logger.warning(
                    "Device %s is probably not a supported device",
                    dev_name
                )
                return

            count = 0
            line = self._read_line(ser)
            while line != "***DONE***" and count < MAX_TRY:
                if line.startswith(f"SENSOR{TTYConnector.SEPARATOR}"):
                    parts = line.split(TTYConnector.SEPARATOR)
                    sensors.append(parts[1])
                    self._logger.debug(
                        "Sensor %s discovered for %s",
                        parts[1],
                        dev_name
                    )
                line = self._read_line(ser)
                count += 1

            if count >= MAX_TRY:
                self._logger.warning(
                    "Device %s is probably not a supported device",
                    dev_name
                )
                return

            if not sensors:
                self._logger.error("Device %s don't declare any sensor", dev_name)


            self._devices[dev_name] = {
                "serial": ser,
                "sensors": sensors
            }
            self._logger.info("Device %s registered", dev_name)
        except OSError:
            self._logger.exception("Error while registring device %s", dev_name)
            self._logger.error("Device %s is not registered", dev_name)

    def _unregister_device(self, dev_name):
        if self._devices[dev_name]["serial"].is_open:
            self._devices[dev_name]["serial"].close()
        del self._devices[dev_name]
        self._logger.info("Device %s unregistred", dev_name)

    def _is_arduino(self, usb_device):
        """Determine if a usb device is an arduino."""

        k_to_check = [
            "ID_VENDOR_FROM_DATABASE", "ID_MODEL_FROM_DATABASE", "ID_SERIAL",
            "ID_VENDOR_ENC", "DEVLINKS", "ID_VENDOR"
        ]
        for key in k_to_check:
            if "arduino" in usb_device.get(key).lower():
                return True

        return False

    def _find_arduinos(self):
        """Search ttys."""

        while True:
            context = pyudev.Context()
            found_devices = []
            for device in context.list_devices(subsystem='tty', ID_BUS='usb'):
                # print(json.dumps(dict(device), indent=4))
                if self._is_arduino(device):
                    dev_name = device.get("DEVNAME")
                    found_devices.append(dev_name)
                    if dev_name not in self._devices:
                        self._register_device(dev_name)
            devices_to_remove = []
            for dev in self._devices:
                if dev not in found_devices:
                    devices_to_remove.append(dev)
            for dev in devices_to_remove:
                self._unregister_device(dev)
            time.sleep(5)


    def on_start(self):
        threading.Thread(
            target=self._find_arduinos
        ).start()


    def supported_sensors(self):
        res = []
        for dev in self._devices.items():
            res += dev[1]["sensors"]

        return res

    def on_command(self, sid, command):
        ser = self._get_serial(sid)
        if ser:
            self._logger.debug(
                "Receive command %s for sensor %s",
                command,
                sid
            )
            command = (
                f'COMMAND{TTYConnector.SEPARATOR}'
                f'SENSOR{TTYConnector.SEPARATOR}'
                f'{sid}{TTYConnector.SEPARATOR}{command}'
                '\n'
            )
            ser.write(command.encode("utf-8"))


    def read_data(self):
        try:
            for dev in self._devices.items():
                if dev[1]["serial"].in_waiting:
                    line = self._read_line(dev[1]["serial"])
                    if line.startswith(f"DATA{TTYConnector.SEPARATOR}"):
                        parts = line.split(TTYConnector.SEPARATOR)
                        sid = parts[1]
                        value = parts[2]
                        return{
                            "sid": sid,
                            "data": value
                        }
        except OSError:
            return None
