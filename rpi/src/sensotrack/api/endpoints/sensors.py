# -*- coding: utf-8 -*-
"""Sensors endpoints."""
import logging

from flask import request
from flask_restx import Resource

from sensotrack import settings
from sensotrack.api.datamodel import SENSOR_VALUE, SENSOR_COMMAND
from sensotrack.api.restx import API
from sensotrack.services.sensors import SensorService
from sensotrack.utils.exceptions import STException

NS = API.namespace(
    name='Sensors',
    path='/',
    description='Sensorts resources'
)


@NS.route(F'{settings.RESTX_BASE_URL_CURRENT}/sensors/<sid>/last')
class OneSensorLast(Resource):
    """Single sensor last value endpoint class."""

    logger = None

    # pylint: disable=keyword-arg-before-vararg
    def __init__(self, api=None, *args, **kwargs):
        Resource.__init__(self, api, kwargs)
        self.logger = logging.getLogger(__name__)

    @API.marshal_with(SENSOR_VALUE)
    @NS.response(404, "Sensor or value not found")
    def get(self, sid):
        """Return last record value for sensor ID."""

        self.logger.info("GET last value from %s", sid)
        svc = SensorService(settings.conf)
        res = svc.get(sid)
        if not res:
            raise STException("Sensor value not found", 404)

        return res

    @API.marshal_with(SENSOR_VALUE)
    @NS.response(404, "Sensor or value not found")
    def post(self, sid):
        """Request a new last value for sensor ID."""

        self.logger.info("GET last value from %s", sid)
        svc = SensorService(settings.conf)
        res = svc.get_new_value(sid)
        if not res:
            raise STException("Sensor value not found", 404)

        return res


@NS.route(F'{settings.RESTX_BASE_URL_CURRENT}/sensors/<sid>')
class OneSensor(Resource):
    """Single sensor endpoint class."""

    logger = None

    # pylint: disable=keyword-arg-before-vararg
    def __init__(self, api=None, *args, **kwargs):
        Resource.__init__(self, api, kwargs)
        self.logger = logging.getLogger(__name__)

    @NS.expect(SENSOR_COMMAND)
    def post(self, sid):
        """Send a command to a sensor."""
        self.logger.debug(request.json)
        svc = SensorService(settings.conf)
        svc.send_command(sid, request.json["command"])
