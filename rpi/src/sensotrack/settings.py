# -*- coding: UTF-8 -*-

"""Sensors mediation layer."""

# --------------------------------------------------------
# Software Name : Sensor Track
#
# 2023 Orange
#
# -------------------------------------------------------
#   Benoit HERARD <benoit.herard(at)orange.com>
# -------------------------------------------------------

# FLASK/RESTX Build time configuration
FLASK_DEBUG = False  # Do not use debug mode in production

# Flask-Restplus settings
# RESTX_SWAGGER_UI_DOC_EXPANSION = 'none'
RESTX_SWAGGER_UI_DOC_EXPANSION = 'list'
# RESTX_SWAGGER_UI_DOC_EXPANSION = 'full'
RESTX_VALIDATE = True
RESTX_MASK_SWAGGER = False
RESTX_ERROR_404_HELP = False

RESTX = {
    "base_url": "/",
    "version": '1.0',
    "title": 'Sensors Track API',
    "description": (
        'Risk Sensors Track API'
    ),
    "binding": "0.0.0.0:8080",
}

RESTX_BASE_URL_CURRENT = "/v1"
RESTX_SUPPORTED_BASE_URL = [RESTX_BASE_URL_CURRENT]

CONFIG_FILES = {
    "app": "sensotract.json",
    "log": "conf/logging.json"
}

data_cleaning = {
    "retention_s": 86400,
    "period": 3600
}

# Runtime configuration
conf = {}  # pylint: disable=invalid-name
