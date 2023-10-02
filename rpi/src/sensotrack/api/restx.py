# -*- coding: UTF-8 -*-
"""Restx library (Flask-resplus fork) configuration and startup."""
import logging

from flask_restx import Api
from werkzeug.exceptions import HTTPException

from sensotrack import settings
from sensotrack.utils.exceptions import STException

LOG = logging.getLogger(__name__)

# Settings for swagger meta API
API = Api(
    version=settings.RESTX["version"],
    title=settings.RESTX["title"],
    description=settings.RESTX["description"],
    doc="/doc/",
)

@API.errorhandler(STException)
def scoring_error_handler(root_exception):
    """Return encountred error in REST compliant way."""
    message = str(root_exception)
    LOG.exception(message)

    if not settings.FLASK_DEBUG:
        return {
            'message':  str(root_exception),
            'description': message,
            'code': root_exception.http_status
        }, root_exception.http_status
    return None
@API.errorhandler
def default_error_handler(root_exception):
    """Return encountred error in REST compliant way."""
    message = (
        "An unhandled exception occurred. "
        F'{type(root_exception).__name__}: {str(root_exception)}'
    )
    LOG.exception(message)

    if not settings.FLASK_DEBUG:
        return {
            'message':  str(root_exception),
            'description': message,
            'code': 500
        }, 500
    return None

@API.errorhandler(HTTPException)
def http_error_handler(http_exception):
    """Return encountred error in REST compliant way."""

    if not settings.FLASK_DEBUG:
        # Use HTTP standard codes, messages and desc. by default
        message = http_exception.name
        description = http_exception.description
        app_code = http_exception.code

        if hasattr(http_exception, "data") and http_exception.data:
            # Exception was raised via an "abort" restx call (typcally "except" on EVException)
            message = http_exception.data["message"]
            if "description" in http_exception.data and http_exception.data["description"]:
                # Use custom desc for payload if any
                description = http_exception.data["description"]
            else:
                http_exception.data["description"] = description
            if "app_code" in http_exception.data:
                # Use custom app_code as code for payload if any
                app_code = http_exception.data["app_code"]
                http_exception.data["code"] = http_exception.data["app_code"]
                del http_exception.data["app_code"]
            http_exception.data["code"] = app_code
        return {
            'message':  message,
            'description': description,
            'code': app_code
        }, http_exception.code
    return None

