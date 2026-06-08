#!/usr/bin/env python3

import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import require_dir, require_file
from common import ensure_dir, run_cmd
from config import DOCKER_NETWORK_NAME, QBIT_CONFIG_PATH, require_config_value
from docker import ensure_network, run_container
from formatting import print_header, print_step

# LAN CIDR — allows WebUI access directly from LAN without going through nginx.
# NOTE: Do NOT add the Docker subnet here — it's the container's own
# directly-attached network and including it causes a route conflict
# in hotio's startup (eth0 is already on the subnet). Container-to-
# container traffic on the docker network bypasses the VPN automatically.
VPN_LAN_CIDR = "192.168.1.0/24"

WG_CONF_SRC = QBIT_CONFIG_PATH / "/wg0.conf"


def main():
    print_header("SETTING UP QBITTORRENT WITH WIREGUARD VPN")

    media_path = require_config_value("MEDIA_SERVICES_PATH")
    qbit_subdomain = require_config_value("QBIT_SUBDOMAIN")

    require_file(str(WG_CONF_SRC), "WireGuard config file (wg0.conf)")
    require_dir(media_path, "Media services path")

    qbit_path = f"{media_path}/qbit-data"
    qbit_wg_dir = f"{qbit_path}/wireguard"
    qbit_wg_target = f"{qbit_wg_dir}/wg0.conf"

    print_step("Creating qBittorrent directories...")
    ensure_dir(qbit_wg_dir)

    print_step("Copying WireGuard config to qBittorrent config directory...")
    run_cmd(f"cp {WG_CONF_SRC} {qbit_wg_target}")

    ensure_network()

    run_container(
        name="qbittorrent",
        opts=[
            "--network",
            DOCKER_NETWORK_NAME,
            "--restart",
            "unless-stopped",
            "--cap-add=NET_ADMIN",
            "-e",
            "PUID=1000",
            "-e",
            "PGID=1000",
            "-e",
            "UMASK=002",
            "-e",
            "TZ=America/Chicago",
            "-e",
            "VPN_ENABLED=true",
            "-e",
            "VPN_CONF=wg0",
            "-e",
            "VPN_PROVIDER=proton",
            "-e",
            "VPN_AUTO_PORT_FORWARD=true",
            "-e",
            "WEBUI_PORTS=8080/tcp",
            "-e",
            "VPN_LAN_LEAK_ENABLED=false",
            "-e",
            "VPN_HEALTHCHECK_ENABLED=false",
            "-e",
            "PRIVOXY_ENABLED=false",
            "-e",
            "UNBOUND_ENABLED=false",
            "-e",
            f"VPN_LAN_NETWORK={VPN_LAN_CIDR}",
            "-v",
            f"{qbit_path}:/config",
            "ghcr.io/hotio/qbittorrent:latest",
        ],
        notes=[
            f"Access qBittorrent WebUI at {qbit_subdomain} if nginx is configured",
            "Validate VPN connection: docker logs qbittorrent",
        ],
    )


if __name__ == "__main__":
    main()
