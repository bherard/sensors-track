# -*- coding: UTF-8 -*-
"""User Scoring API datamodel description."""
from flask_restx import fields
from sensotrack.api.restx import API
from sensotrack import settings

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
