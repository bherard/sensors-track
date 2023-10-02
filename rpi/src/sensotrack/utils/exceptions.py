
"""Sensors mediation layer."""

# --------------------------------------------------------
# Software Name : Sensor Track
#
# 2023 Orange
#
# -------------------------------------------------------
#   Benoit HERARD <benoit.herard(at)orange.com>
# -------------------------------------------------------

class STException(Exception):
    """EventHistory Exception."""

    message = None
    http_status = -1
    app_code = -1
    description = None

    def __init__(self, message, http_status=500, app_code=None, description=None):
        """Initialize exception.

        :param message: Exception message
        :type message: str
        :param http_status: Resulting HTTP Status
        :type http_status: int
        """
        Exception.__init__(self, message)
        self.http_status = http_status
        self.message = message
        self.description = description
        if app_code:
            self.app_code = app_code
        else:
            self.app_code = http_status
