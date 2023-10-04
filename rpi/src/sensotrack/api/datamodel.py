# -*- coding: UTF-8 -*-
"""User Scoring API datamodel description."""
from flask_restx import fields
from sensotrack.api.restx import API

ERROR = API.model("Error", {
    'message': fields.String(
        required=True,
        decription="Error message"
    ),
    'description': fields.String(
        required=True,
        decription="Error message description"
    ),
    "code": fields.Integer(
        required=True,
        decription="Error code"
    ),
    "errors": fields.Raw(
        required=False,
        description="JSON Object with errors detected",
        example="{\"user_id\": \"'user_id' is a required property\"}"
    )
})
API_STATUS = API.model('ServerStatus', {
    'status': fields.String(
        required=True,
        decription='API Server status'
    ),
    'pingers': fields.List(
        fields.String(
            required=True,
            description="Pinger status (i.e. subsystems status)",
            example="Subsystem status message"
        ),
        required=False,
    )
})

SENSOR_VALUE =  API.model('SensorValue', {
    "sensorId": fields.String(
        required=True,
        description="Sensor Identifier"
    ),
    'value': fields.String(
        required=True,
        description="Sensort value"
    ),
    "measurementDate": fields.String(
        required=True,
        description="Measurement date using ISO format"
    )
})
SENSOR_COMMAND = API.model('SensorCommand', {
    "command": fields.String(
        required=True,
        description="Command to send to sensor"
    )
})
