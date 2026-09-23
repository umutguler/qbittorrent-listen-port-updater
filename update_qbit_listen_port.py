#!/usr/bin/env python3
"""Keep qBittorrent's listening port in sync with the port forwarded by Gluetun. Configured via env vars."""
import logging
import os
import signal
import sys
import time
from pathlib import Path

import qbittorrentapi

logger = logging.getLogger("port-tool")
# Present only while the last check succeeded; used by the container healthcheck.
HEALTH_FILE = Path("/tmp/healthy")


def sync(client, port_file):
    """One check. HEALTH_FILE exists afterwards only if it succeeded; failures (e.g. Gluetun reconnecting,
    qBittorrent restarting) are logged and retried next interval."""
    try:
        vpn_port = int(Path(port_file).read_text(encoding="utf-8"))
        current_port = client.app.preferences["listen_port"]
        if vpn_port != current_port:
            client.app.set_preferences({"listen_port": vpn_port})
            logger.info("Updated qBittorrent listening port %s -> %s", current_port, vpn_port)
        HEALTH_FILE.touch()
    except (OSError, ValueError, qbittorrentapi.APIError) as e:
        logger.warning("Check failed, will retry: %s: %s", type(e).__name__, e)
        HEALTH_FILE.unlink(missing_ok=True)


def main():
    logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S",
                        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
    # qbittorrentapi/urllib3 log every internal retry with a full stack; our own warning is enough.
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    # As PID 1 in a container SIGTERM is ignored unless handled; exit promptly on `docker stop`.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

    env = os.environ.get
    port_file = env("VPN_PORT_FILE", "/tmp/gluetun/forwarded_port")
    interval = float(env("INTERVAL_MINUTES", "5"))
    client = qbittorrentapi.Client(
        host=f"http://{env('QBIT_HOST', '127.0.0.1')}:{env('QBIT_PORT', '9500')}",
        username=os.environ["QBIT_USERNAME"],
        password=os.environ["QBIT_PASSWORD"],
        REQUESTS_ARGS={"timeout": (5, 30)},
    )

    logger.info("Checking %s every %g minute(s).", port_file, interval)
    while True:
        sync(client, port_file)
        time.sleep(interval * 60)


if __name__ == "__main__":
    main()
