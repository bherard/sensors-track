import threading
import unittest
import json

import mock
import requests
from werkzeug.serving import make_server

from sensotrack.app import APP, load_config
from sensotrack import settings

class ServerThread(threading.Thread):
    """Mock Flask server."""

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', 8080, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        """Start web server and flask app."""
        self.server.serve_forever()

    def shutdown(self):
        """Stop web server and flask app."""
        self.server.shutdown()


class TestFlaskAPI(unittest.TestCase):
    """Test common errors return codes."""

    _server = None

    @classmethod
    @mock.patch("sensotrack.app.Receiver", mock.MagicMock())
    @mock.patch("sensotrack.app.SensorService", mock.MagicMock())
    @mock.patch("sensotrack.app.ConnectorsManager", mock.MagicMock())
    def setUpClass(cls) -> None:
        load_config()
        cls._server = ServerThread(APP)
        cls._server.start()
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._server.shutdown()
        return super().tearDownClass()

    def _is_json(self, data):
        if not data:
            return False
        try:
            json.loads(data)
        except Exception:  # pylint: disable=broad-except
            return False
        return True

    def _assert_error_structure(self, req_resp, expected_code):
        self.assertEqual(req_resp.status_code, expected_code)
        self.assertTrue(self._is_json(req_resp.text))
        self.assertIn("code", req_resp.json())
        self.assertIn("message", req_resp.json())
        self.assertIn("description", req_resp.json())

    def test_unknow_resource(self):
        """Test return on unknown resource call."""
        resp = requests.get(
            "http://localhost:8080/random-url",
            headers={"Accept": "application/json"},
            timeout=10
        )
        self._assert_error_structure(resp, 404)

    def test_method_not_allowed(self):
        """Test return on method not allowed call.

            i.e method is not exiting at RestX Resource level.
        """
        resp = requests.delete(
            "http://localhost:8080/v1/status",
            headers={"Accept": "application/json"},
            timeout=10
        )
        self._assert_error_structure(resp, 405)

    def test_method_invalid_accept(self):
        """Test return with invalid Accept header."""
        resp = requests.get(
            "http://localhost:8080/v1/status",
            headers={"Accept": "application/xml"},
            timeout=10
        )
        self._assert_error_structure(resp, 406)

    def test_method_invalid_content_type(self):
        """Test return with invalid content type header."""
        resp = requests.post(
            "http://localhost:8080/v1/sensors/fake-sensor",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/xml",
            },
            data='{}',
            timeout=10
        )
        self._assert_error_structure(resp, 415)

    def test_status(self):
        """Test /v1/status endpoint."""
        resp = requests.get(
            "http://localhost:8080/v1/status",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=10
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "OK")


    @mock.patch("paho.mqtt.client.Client")
    def test_send_command(self, mqtt_mock):
        """Test POST /v1/sensors/{sid} (cend command)."""

        resp = requests.post(
            "http://localhost:8080/v1/sensors/random-sensor",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json={
                "command": "random-command"
            },
            timeout=10
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(mqtt_mock.return_value.publish.called)
        self.assertEqual(
            mqtt_mock.return_value.publish.call_args[0][0],
            'sensors/command/random-sensor'
        )
        self.assertEqual(
            mqtt_mock.return_value.publish.call_args[0][1],
            'random-command'
        )

    @mock.patch("sensotrack.dao.os.path.exists", mock.Mock(return_value=False))
    def test_get_last_not_found(self):
        "Test GET /v1/sensors/{sid}/last (get last not found)"

        resp = requests.get(
            "http://localhost:8080/v1/sensors/random-sensor/last",
            headers={
                "Accept": "application/json",
            },
            timeout=10
        )
        self.assertEqual(resp.status_code, 404)

    @mock.patch(
        "sensotrack.dao.SensorDAO.get",
        mock.Mock(
            return_value={
                "sensorId": "random-sensor",
                "value": "42",
                "measurementDate": "2023-10-03T05:27:40.464057+00:00"
            }
        )
    )
    def test_get_last_found(self):
        "Test GET /v1/sensors/{sid}/last (get last found)"

        resp = requests.get(
            "http://localhost:8080/v1/sensors/random-sensor/last",
            headers={
                "Accept": "application/json",
            },
            timeout=10
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["value"], "42")
    
    @mock.patch(
        "sensotrack.services.sensors.SensorDAO"
    )
    @mock.patch("sensotrack.services.sensors.time.sleep", mock.MagicMock())
    def test_post_last(self, doa_mock):
        "Test POST /v1/sensors/{sid}/last (get new)"

        class SensorDOAMock():
            call_count = 0

            def get(self, sid):
                if SensorDOAMock.call_count == 0:
                    SensorDOAMock.call_count +=1
                    return {
                        "sensorId": "random-sensor",
                        "value": "42",
                        "measurementDate": "2023-10-03T05:27:40.464057+00:00"
                    }
                else:
                    SensorDOAMock.call_count +=1
                    return {
                        "sensorId": "random-sensor",
                        "value": "69",
                        "measurementDate": "2123-10-03T05:27:40.464057+00:00"
                    }

        doa_mock.return_value = SensorDOAMock()
        resp = requests.post(
            "http://localhost:8080/v1/sensors/random-sensor/last",
            headers={
                "Accept": "application/json",
            },
            timeout=10
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["value"], "69")
        self.assertGreater(SensorDOAMock.call_count, 1)
