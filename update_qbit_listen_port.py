#!/usr/bin/env python3
"""Auto-Update qBittorrent listening port based on the port forwarded by VPN."""
import enum
import logging
import sys
import argparse
import qbittorrentapi


@enum.unique
class ToolExitCodes(enum.IntEnum):
    """Exit codes for the tool"""
    ALL_GOOD = 0
    BASE_ERROR = 1
    QBIT_AUTH_FAILURE = 2
    HTTP_ERROR = 3
    INVALID_PORT = 4
    QBIT_PREF_MISSING = 5
    FILE_NOT_FOUND = 6


def get_args():
    """Get command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Update qBittorrent listening port based on the port forwarded by VPN."
    )
    parser.add_argument(
        "--host", type=str, default="localhost",
        help="Hostname or IP address of the qBittorrent WebUI"
    )
    parser.add_argument(
        "--port", type=int, default=9500,
        help="Port number of the qBittorrent WebUI"
    )
    parser.add_argument(
        "--username", type=str, required=True,
        help="Username for qBittorrent WebUI"
    )
    parser.add_argument(
        "--password", type=str, required=True,
        help="Password for qBittorrent WebUI"
    )
    parser.add_argument(
        "--vpn-port-file", type=str, default="/tmp/gluetun/forwarded_port",
        help="Path to the VPN's forwarded port file"
    )
    return parser.parse_args()


def main():
    """Main function. Connects to qBittorrent and updates the listening port."""
    args = get_args()

    # Initialize logging
    logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S",
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    logger = logging.getLogger("port-tool")

    # Try to read the forwarded port from file
    try:
        with open(args.vpn_port_file, 'r', encoding='utf-8') as file:
            vpn_port = int(file.read().strip())
    except FileNotFoundError:
        logger.error("File %s not found.", args.vpn_port_file)
        sys.exit(ToolExitCodes.FILE_NOT_FOUND)

    # Connect to qBittorrent and fetch/update settings
    try:
        qbt_client = qbittorrentapi.Client(
            host=f'http://{args.host}:{args.port}',
            username=args.username,
            password=args.password
        )
        qbt_client.auth_log_in()

        logger.info('qBittorrent: %s', qbt_client.app.version)
        logger.info('qBittorrent Web API: %s', qbt_client.app.web_api_version)

        current_port = qbt_client.app.preferences["listen_port"]
        if vpn_port != current_port:
            qbt_client.app.set_preferences(
                {"listen_port": vpn_port})
            logger.info(
                "Updated qBittorrent listening port to %s", vpn_port)
        else:
            logger.info("Ports matched, no change required.")

    except qbittorrentapi.LoginFailed as e:
        logger.error(str(e))
        sys.exit(ToolExitCodes.QBIT_AUTH_FAILURE)
    except KeyError:
        logger.error(
            "Preference 'listen_port' not found in qBittorrent settings.")
        sys.exit(ToolExitCodes.QBIT_PREF_MISSING)

    sys.exit(ToolExitCodes.ALL_GOOD)


if __name__ == "__main__":
    main()
