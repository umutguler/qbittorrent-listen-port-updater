# qBittorrent forward-port-updater

Fork off an existing project that includes some updates + a dockerfile to be deployed as a container.
This is a small python script to update qbittorrent's port forwarding from glueetun, as gluetun doesn't keep the port static.
You can also find the image on dockerhub at [uguler/qbittorrent-port-updater](uguler/qbittorrent-port-updater)

## Requirements
You have to edit your Gluetun container configuration adding new volume:

`/select/any/host/path:/tmp/gluetun`

In the Gluetun container folder `/tmp/gluetun` you can find the files `forwarded_port` and `ip` which contains, as the names say, the forwarded port chosen by the vpn provider, and the vpn IP.

```
pip install qbittorrent-api
pip install requests
```

## Configuration
Change the qBittorrent endpoint matching your own ip/domain and update credentials to login qBittorrent, this is required in order to update its settings.

Last step you can do is to setup a cronjob to auto execute this script in order to keep the port synced to the forwarded one.

Using `crontab -e` add this to run the script hourly:
```
0 * * * * /usr/bin/python3 /your/path/port-sync.py >> /var/log/qbittorrent_port_sync.log 2>&1
```

PS: remember whenever you re-deploy Gluetun container you have to re assign it under network configuration mode as `container:<gluetun_service_id>` or if you use Portainer or similar, you have to re-select Gluetun container
