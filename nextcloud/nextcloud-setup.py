#!/usr/bin/env python3

import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import require_dir
from common import ensure_dir
from config import DOCKER_NETWORK_NAME, require_config_value
from docker import ensure_network, run_container
from formatting import print_header, print_info, print_step


def main():
    print_header("SETTING UP NEXTCLOUD ALL-IN-ONE")

    core_path = require_config_value("CORE_SERVICES_PATH")
    require_dir(core_path, "Core services path")

    nextcloud_data_dir = f"{core_path}/nextcloud-data"

    print_step(
        f"Creating Nextcloud data directory at {nextcloud_data_dir}..."
    )
    ensure_dir(nextcloud_data_dir)

    ensure_network()

    print_info(
        "Using latest release — see https://github.com/nextcloud/all-in-one#how-to-switch-the-channel to change channel"
    )

    run_container(
        name="nextcloud-aio-mastercontainer",
        opts=[
            "--init",
            "--sig-proxy=false",
            "--network",
            DOCKER_NETWORK_NAME,
            "--restart",
            "always",
            "--env",
            "APACHE_PORT=11000",
            "--env",
            "APACHE_IP_BINDING=0.0.0.0",
            "--env",
            f"APACHE_ADDITIONAL_NETWORK={DOCKER_NETWORK_NAME}",
            "--env",
            "SKIP_DOMAIN_VALIDATION=true",
            "--env",
            f"NEXTCLOUD_DATADIR={nextcloud_data_dir}",
            "--volume",
            "nextcloud_aio_mastercontainer:/mnt/docker-aio-config",
            "--volume",
            "/var/run/docker.sock:/var/run/docker.sock:ro",
            "ghcr.io/nextcloud-releases/all-in-one:latest",
        ],
        notes=[
            "Access Nextcloud AIO at https://<server-ip>:11000 (NOT the subdomain — nginx must proxy to the AIO container)",
            "Complete the initial setup through the web interface",
            f"Data will be stored in {nextcloud_data_dir}",
        ],
    )


if __name__ == "__main__":
    main()
