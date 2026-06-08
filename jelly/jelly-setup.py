#!/usr/bin/env python3

import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import require_dir
from common import ensure_dir
from config import DOCKER_NETWORK_NAME, require_config_value
from docker import ensure_network, run_container
from formatting import print_header, print_step


def main():
    print_header("SETTING UP JELLYFIN MEDIA SERVER")

    media_path = require_config_value("MEDIA_SERVICES_PATH")
    jelly_subdomain = require_config_value("JELLY_SUBDOMAIN")

    require_dir(media_path, "Media services path")

    jelly_config_dir = f"{media_path}/jelly/config"
    jelly_cache_dir = f"{media_path}/jelly/cache"
    jelly_media_dir = f"{media_path}/jelly/media"

    print_step("Creating Jellyfin directories...")
    ensure_dir(jelly_config_dir)
    ensure_dir(jelly_cache_dir)
    ensure_dir(jelly_media_dir)

    ensure_network()

    run_container(
        name="jellyfin",
        opts=[
            "--network",
            DOCKER_NETWORK_NAME,
            "--volume",
            f"{jelly_config_dir}:/config",
            "--volume",
            f"{jelly_cache_dir}:/cache",
            "--mount",
            f"type=bind,source={jelly_media_dir},target=/media",
            "--restart",
            "unless-stopped",
            "jellyfin/jellyfin:latest",
        ],
        notes=[
            f"Access Jellyfin at {jelly_subdomain} if nginx is configured",
            f"Add media files to {jelly_media_dir}",
            "Use --net=host instead of --network to enable DLNA device discovery if needed",
        ],
    )


if __name__ == "__main__":
    main()
