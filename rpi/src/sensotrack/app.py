#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""app.py: Sesnors medation web app"""

# --------------------------------------------------------
# Software Name : Sensor Track
#
# 2023 Orange
#
# -------------------------------------------------------
#   Benoit HERARD <benoit.herard(at)orange.com>
# -------------------------------------------------------
import argparse
import json
import logging

import flask_restx.apidoc
import flask
from flask import Blueprint, Flask, request
from werkzeug.exceptions import NotAcceptable, HTTPException, UnsupportedMediaType

from sensotrack import settings, __version__
from sensotrack.utils import load_conf, dirname
from sensotrack.utils.logging import LoggingConfig

APP = Flask(__name__)


def _is_restx_resource(full_path: str) -> bool:
    for rest_path in settings.RESTX_SUPPORTED_BASE_URL:
        if full_path.startswith(rest_path):
            return True
    return False

def configure_app(flask_app):
    """Load application configuration to flask.

    Load configuration to Flask object
        :param flask_app: Flask application to configure
        :type flask_app: Flask
    """
    flask_app.config[
        'SWAGGER_UI_DOC_EXPANSION'
    ] = settings.RESTX_SWAGGER_UI_DOC_EXPANSION

    flask_app.config[
        'RESTX_VALIDATE'
    ] = settings.RESTX_VALIDATE

    flask_app.config[
        'RESTX_MASK_SWAGGER'
    ] = settings.RESTX_MASK_SWAGGER

    flask_app.config[
        'RESTX_ERROR_404_HELP'
    ] = settings.RESTX_ERROR_404_HELP

    flask_app.config[
        'APPLICATION_ROOT'
    ] = settings.RESTX["base_url"]


def initialize_app(flask_app):
    """Apply application configuration.

    Load configuration to Flask object and apply configuration to it
        :param flask_app: Flask application to configure
        :type flask_app: Flask
    """
    configure_app(flask_app)


    # Import endpoints to generate Swagger at Flask init
    # Imports a AFTER load_config() to ensure SUPPORTED_EVENT_TYPES is populated form config
    # pylint: disable=import-outside-toplevel
    from sensotrack.api.endpoints.admin import NS as admin_ns  # pylint: disable=unused-import
    # from scoring.api.endpoints.session_risk import NS as session_ns  # pylint: disable=unused-import
    # from scoring.api.endpoints.user_risk import NS as user_ns  # pylint: disable=unused-import
    # from scoring.api.endpoints.event_risk import NS as event_ns  # pylint: disable=unused-import


    # Define base_url for the app
    from sensotrack.api.restx import API as api
    blueprint = Blueprint('api', __name__,
                          url_prefix=settings.RESTX["base_url"])
    api.init_app(blueprint)

    # Define base_url from swaggerui resources (js, css...)
    api_doc = flask_restx.apidoc.apidoc
    api_doc.url_prefix = settings.RESTX["base_url"] + "/doc"

    flask_app.register_blueprint(blueprint)

@APP.errorhandler(HTTPException)
def handle_exception(exc):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = exc.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": exc.code,
        "message": exc.name,
        "description": exc.description,
    })
    response.content_type = "application/json"
    return response

@APP.before_request
def before_request():
    """Execute actions before each HTTP requests."""
    # Content negociation control
    if _is_restx_resource(request.full_path):
        if "Accept" in request.headers \
            and not (
                "json" in request.headers["Accept"] \
                or "*/*" in request.headers["Accept"]
            ):
            raise NotAcceptable(
                "The Accept incoming header does not match any available content-type."
            )
        if "Content-Type" in request.headers and "json" not in request.headers["Content-Type"]:
            raise  UnsupportedMediaType(
                "The format of the posted body is not supported by the endpoint."
            )

@APP.after_request
def after_request(response: flask.Response):
    """Add CORS Headers and log execution."""

    response.headers.add(
        'Access-Control-Allow-Origin',
        '*'
    )
    response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type,Authorization'
    )
    response.headers.add(
        'Access-Control-Allow-Methods',
        'GET,PUT,POST,DELETE'
    )
    response.headers.add(
        "X-Clacks-Overhead",
        "GNU Terry Pratchett"
    )
    return response


def main():
    """Standalone application launcher."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-version',
        action="store_true",
        default=False,
        help="display version and exit"
    )
    args = parser.parse_args()

    if args.version:
        print(F"Version: {__version__}")
        return


    load_config()
    server_binding = settings.RESTX["binding"].split(':')
    APP.run(
        debug=settings.FLASK_DEBUG,
        port=int(server_binding[1]),
        host=server_binding[0],
        threaded=True
    )


def load_config():
    """Load application config and init."""


    settings.conf = load_conf(settings.CONFIG_FILES["app"])
    LoggingConfig.configure_logging(
        settings.conf,
        f'{dirname(__file__)}/{settings.CONFIG_FILES["log"]}',
        __version__
    )

    logger = logging.getLogger(__name__)
    logger.debug("APP Is configured")

    initialize_app(APP)



if __name__ == "__main__":
    main()
