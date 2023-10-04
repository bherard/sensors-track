"""Data access layer"""

import logging
import json
import os

class SensorDAO:
    """DAO for sensors."""
    def __init__(self, conf) -> None:
        self._conf = conf
        self._logger = logging.getLogger(__name__)

    def get(self, sid):
        """Get a sensor by id

        :param sid: sensor id
        :type sid: str
        :return: sensor data if found None else.
        :rtype: dict
        """

        res = None
        data_file_name = f'{self._conf["datadir"]}/{sid}.json'
        if os.path.exists(data_file_name):
            with open(data_file_name, "r", encoding="utf-8") as data_file:
                res = json.load(data_file)

        return res

    def upsert(self, sensor):
        """Persist sensor

        :param sensor: sensor to persist
        :type sensor: dict
        """

        data_file_name = f'{self._conf["datadir"]}/{sensor["sensorId"]}.json'
        with open(data_file_name, "w", encoding="utf-8") as data_file:
            data_file.write(f'{json.dumps(sensor)}')

    def delete(self, sid):
        """Delet sensor data

        :param sid: sensor identifier
        :type sid: str
        """
        data_file_name = f'{self._conf["datadir"]}/{sid}.json'
        if os.path.exists(data_file_name):
            os.remove(data_file_name)
