
import logging
import time
import unittest

import mock
import paho.mqtt.client as mqtt

from sensotrack.services.connectors.serial import SerialConnector

class SerialMock:

    _read_buffer = []

    def write(self, data):
        
        str_data = data.decode("utf-8")
        if str_data.startswith(f'COMMAND{SerialConnector._SEPARATOR}SENSORS\n'):
            self._read_buffer.append(
                "***START***\n".encode("utf-8")
            )
            self._read_buffer.append(
                f"SENSOR{SerialConnector._SEPARATOR}SENSOR1\n".encode("utf-8")
            )
            self._read_buffer.append(
                f"SENSOR{SerialConnector._SEPARATOR}SENSOR2\n".encode("utf-8")
            )
            self._read_buffer.append(
                "***DONE***\n".encode("utf-8")
            )
        else:
            self._read_buffer.append(data)

    @property
    def is_open(self):
        return True

    @property
    def in_waiting(self):
        return len(self._read_buffer) > 0
    
    def readline(self):
        line = None
        if len(self._read_buffer) > 0:
            line = self._read_buffer[0]
            self._read_buffer.remove(line)
        return line
    
    def close(self):
        pass
    

class UsbDeviceMock:
    _def = {
        "DEVNAME": "/dev/ttyX",
        "ID_VENDOR_FROM_DATABASE": "arduino"
    }
    def __init__(self, dev) -> None:
        self._def["DEVNAME"] = dev

    def get(self, key):
        if key in self._def:
            return self._def[key]
        return None
    
class TestSerialConnector(unittest.TestCase):
    """Test Serial connector."""

    def test_start_stop(self):
        """Test start and stop."""

        conf = {
            "mqtt": {
                "host": "localhost",
                "port": 1883
            }
        }
        connector = SerialConnector(conf)
        connector.DISCOVERY_PERIOD = 0.1
        connector.start()
        time.sleep(0.1)
        connector.stop()
        connector.join()

    
    @mock.patch("serial.Serial")
    @mock.patch("pyudev.Context")
    def test_discovery(self, udev_context_mock, serial_mock):

        udev_context_mock.return_value.list_devices.return_value = [
            UsbDeviceMock("/dev/ttyX")
        ]
        serial_mock.return_value = SerialMock()

        conf = {
            "mqtt": {
                "host": "localhost",
                "port": 1883
            }
        }
        connector = SerialConnector(conf)
        connector.DISCOVERY_PERIOD = 0.1
        connector.start()
        time.sleep(0.2)
        connector.stop()
        connector.join()

        self.assertTrue(udev_context_mock.return_value.list_devices.called)
        self.assertTrue(serial_mock.called)
        self.assertIn("/dev/ttyX", connector._devices)
        self.assertIn("SENSOR1", connector._devices["/dev/ttyX"]["sensors"])
        self.assertIn("SENSOR2", connector._devices["/dev/ttyX"]["sensors"])

    @mock.patch("sensotrack.services.connectors.CommandReceiver.publish")
    @mock.patch("serial.Serial")
    @mock.patch("pyudev.Context")
    def test_data_from_device(self, udev_context_mock, serial_mock, publish_mock):

        udev_context_mock.return_value.list_devices.return_value = [
            UsbDeviceMock("/dev/ttyY")
        ]
        serial = SerialMock()
        serial_mock.return_value = serial

        conf = {
            "mqtt": {
                "host": "localhost",
                "port": 1883
            }
        }
        connector = SerialConnector(conf)
        connector.DISCOVERY_PERIOD = 0.1

        connector.start()
        time.sleep(0.2)

        serial.write(f"DATA{connector._SEPARATOR}SENSOR1{connector._SEPARATOR}ipsum".encode("utf-8"))
        serial.write(f"DATA{connector._SEPARATOR}SENSOR2{connector._SEPARATOR}lorem".encode("utf-8"))
        time.sleep(0.2)

        connector.stop()
        connector.join()

        self.assertEqual(publish_mock.call_count, 2)
        self.assertEqual(publish_mock.call_args_list[0][0][0], 'sensors/data/SENSOR1')
        self.assertEqual(publish_mock.call_args_list[0][0][1], "ipsum")
        self.assertEqual(publish_mock.call_args_list[1][0][0], 'sensors/data/SENSOR2')
        self.assertEqual(publish_mock.call_args_list[1][0][1], "lorem")

    @mock.patch("sensotrack.services.connectors.serial.SerialConnector._get_serial")
    def test_command_from_remote(self, serial_mock):


        conf = {
            "mqtt": {
                "host": "localhost",
                "port": 1883
            }
        }
        connector = SerialConnector(conf)
        connector.on_command("SENSOR1","foo")
        self.assertEqual(
            serial_mock.return_value.write.call_args[0][0],
            b'COMMAND/:/SENSOR/:/SENSOR1/:/foo\n'
        )
