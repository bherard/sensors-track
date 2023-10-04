# -*- coding: utf-8 -*-
"""Sensors service."""
import datetime
import logging
import os
import threading
import time

import paho.mqtt.client as mqtt

from sensotrack.dao import SensorDAO

class SensorService:
    """Sensor business implem."""

    POLLING_PERIOD = 0.1
    POLLING_COUNT = 50

    def __init__(self, conf) -> None:
        self._conf = conf
        self._logger = logging.getLogger(__name__)
        self._sensor_dao = SensorDAO(conf)


    def get(self, sid):
        """Get a sensor by id

        :param sid: sensor id
        :type sid: str
        :return: sensor data if found None else.
        :rtype: dict
        """
        return self._sensor_dao.get(sid)

    def register_new_value(self, sid, value):
        """Register a new value from a sensor.

        :param sid: Sensor idenfier
        :type sid: str
        :param value: sensor value
        :type value: float
        """

        sensor = {
            "sensorId": sid,
            'value': value,
            "measurementDate": datetime.datetime.utcnow().replace(
                tzinfo=datetime.timezone.utc
            ).isoformat()
        }
        self._sensor_dao.upsert(sensor)

    def get_new_value(self, sid):
        """Request a new measurement to sensor and return it

        :param sid: Sensor identifier
        :type sid: str
        :return: new sensor measurement
        :rtype: str
        """

        last = self._sensor_dao.get(sid)
        if last:
            last_ts = datetime.datetime.fromisoformat(last["measurementDate"])
        else:
            last_ts = 0

        count = 0
        res = None
        while not res and count < SensorService.POLLING_COUNT:
            time.sleep(SensorService.POLLING_PERIOD)
            last = self._sensor_dao.get(sid)
            if last \
                and datetime.datetime.fromisoformat(last["measurementDate"]) > last_ts:
                res = last
                break

            count += 1

        return res

    def send_command(self, sid, command):
        """Send a command to a sensor."


        :param sid: _description_
        :type sid: _type_
        :param command: _description_
        :type command: _type_
        """

        mqtt_client = mqtt.Client(
            "mqttPublisher." + str(time.time()),
            False
        )
        mqtt_client.connect(
            self._conf["mqtt"]["host"],
            self._conf["mqtt"]["port"],
            60
        )
        mqtt_client.publish(
            f"sensors/command/{sid}",
            command
        )

    def _data_cleaner_impl(self):
        while True:
            self._logger.info("Data cleaning is starting....")
            cur_ts = datetime.datetime.now().timestamp()
            for fname in os.listdir(self._conf["datadir"]):
                file_ts = os.path.getmtime(
                    f'{self._conf["datadir"]}/{fname}'
                )
                if (cur_ts - file_ts) > self._conf["dataCleaning"]["retention_s"]:
                    self._logger.debug(
                        "Removing data file %s/%s",
                        self._conf["datadir"],
                        fname
                    )
                    os.remove(f'{self._conf["datadir"]}/{fname}')
            time.sleep(self._conf["dataCleaning"]["period"])

    def start_data_cleaner(self):
        """Start data clener thread."""
        threading.Thread(
            target=self._data_cleaner_impl,
            daemon=True
        ).start()
