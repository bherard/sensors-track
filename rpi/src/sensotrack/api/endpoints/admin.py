# -*- coding: utf-8 -*-
"""Risk scoring admin endpoints."""
import logging

from flask_restx import Resource

from sensotrack import settings
from sensotrack.api.datamodel import API_STATUS
from sensotrack.api.restx import API

NS = API.namespace(
    name='Admin',
    path='/',
    description='Administration resources'
)


@NS.route(F'{settings.RESTX_BASE_URL_CURRENT}/status')
class Ping(Resource):
    """API monitoring Ping class."""

    logger = None

    # pylint: disable=keyword-arg-before-vararg
    def __init__(self, api=None, *args, **kwargs):
        Resource.__init__(self, api, kwargs)
        self.logger = logging.getLogger(__name__)

    @API.marshal_with(API_STATUS)
    @NS.response(503, "System unavailable")
    def get(self):
        """Return API status."""

        self.logger.info("Admin.ping")
        res = {
            "status": "OK",
            "pingers": []
        }
        status = 200

        return res, status
