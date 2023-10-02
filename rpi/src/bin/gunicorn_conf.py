"""Config for gunicorn."""
import gunicorn

import sensotrack.app

gunicorn.SERVER_SOFTWARE = ''

def post_fork(server, worker):  # pylint: disable=unused-argument
    """Triggered by master after a worker has been spawned."""
    sensotrack.app.load_config()
