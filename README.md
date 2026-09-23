# qBittorrent forward-port-updater

Fork of [AlbyGNinja/port-sync](https://github.com/AlbyGNinja/port-sync). Keeps qBittorrent's listening port in sync
with the port forwarded by [Gluetun](https://github.com/qdm12/gluetun), since Gluetun doesn't keep the port static.

Image: `ghcr.io/umutguler/qbittorrent-listen-port-updater:latest` (linux/amd64, linux/arm64).

## Usage
Mount Gluetun's `/tmp/gluetun` to a host path so this tool can read its `forwarded_port` file, then add the
service from [`docker-compose.yml`](docker-compose.yml) to the stack that defines your `gluetun` and `qbittorrent`
services.

| Variable           | Default                        | Description                           |
|--------------------|--------------------------------|---------------------------------------|
| `QBIT_HOST`        | `127.0.0.1`                    | qBittorrent WebUI host                |
| `QBIT_PORT`        | `9500`                         | qBittorrent WebUI port                |
| `QBIT_USERNAME`    | *(required)*                   | WebUI username                        |
| `QBIT_PASSWORD`    | *(required)*                   | WebUI password                        |
| `VPN_PORT_FILE`    | `/tmp/gluetun/forwarded_port`  | Gluetun forwarded port file           |
| `INTERVAL_MINUTES` | `5`                            | Minutes between checks                |

Keep credentials in your orchestrator's secret store or a git-ignored `.env` (see `.env.example`).

Failed checks (Gluetun reconnecting, qBittorrent restarting) log one warning and retry next interval. The container
is **healthy** while the last check succeeded.

Remember: whenever you re-deploy Gluetun, re-attach dependent containers to its network
(`container:<gluetun_service_id>`, or re-select it in Portainer).

## Development
```
npm run build   # build qbittorrent-listen-port-updater:local
npm test        # run the unit tests inside that image
npm start       # run it with ./.env and ./gluetun mounted as /tmp/gluetun
```

Pushes to `main` publish `:latest`; a `v1.2.3` tag also publishes `:1.2.3`.
