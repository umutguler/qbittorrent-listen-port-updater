"""Run: npm test"""
import tempfile
from pathlib import Path
from types import SimpleNamespace

import qbittorrentapi

import update_qbit_listen_port as tool

tmp = Path(tempfile.mkdtemp())
tool.HEALTH_FILE = tmp / "healthy"


class FakeApp:
    def __init__(self, port, error=None):
        self.preferences, self.error = {"listen_port": port}, error

    def set_preferences(self, prefs):
        if self.error:
            raise self.error
        self.preferences.update(prefs)


def check(file_content, qbit_port, error=None):
    """Returns (healthy, qBittorrent port after the check)."""
    port_file = tmp / "forwarded_port"
    port_file.write_text(file_content)
    client = SimpleNamespace(app=FakeApp(qbit_port, error))
    tool.sync(client, port_file)
    return tool.HEALTH_FILE.exists(), client.app.preferences["listen_port"]


assert check("51234\n", 6881) == (True, 51234)      # updates
assert check("51234", 51234) == (True, 51234)       # no-op
assert check("", 6881) == (False, 6881)             # Gluetun mid-reconnect: empty file -> unhealthy
assert check("51234", 6881) == (True, 51234)        # recovers -> healthy again
assert check("51234", 6881, qbittorrentapi.APIConnectionError("down")) == (False, 6881)
tool.HEALTH_FILE.touch()
tool.sync(SimpleNamespace(app=FakeApp(1)), tmp / "missing")
assert not tool.HEALTH_FILE.exists()                # missing file -> unhealthy
print("ok")
