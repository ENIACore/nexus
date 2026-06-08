#!/usr/bin/env python3

import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import require_dir
from common import copy_path, ensure_dir
from config import (
    DOCKER_NETWORK_NAME,
    NGINX_CONFIG_PATH,
    require_config_value,
)
from docker import ensure_network, run_container
from formatting import print_header, print_step

NGINX_LOG_DIR = "/var/log/nginx"
NGINX_VAR_DIR = "/var/www/server"
NGINX_SRC_PATH = NGINX_CONFIG_PATH / "nginx"

# Static IP for the proxy container — must be within DOCKER_NETWORK_SUBNET
# and reserved so no other container is assigned this address
NGINX_CONTAINER_IP = "172.20.0.254"


def copy_nginx_config() -> None:
    print_step("Copying nginx configuration to {NGINX_CONFIG_PATH}...")
    for subdir in [
        "conf",
        "conf.d",
        "snippets",
        "sites-available",
        "streams-available",
    ]:
        copy_path(NGINX_SRC_PATH / subdir, NGINX_CONFIG_PATH / subdir)

    for subdir in ["sites-enabled", "streams-enabled"]:
        print_step(f"Creating {NGINX_CONFIG_PATH / subdir}...")
        ensure_dir(str(NGINX_CONFIG_PATH / subdir))


def main():
    print_header("CREATING SERVER REVERSE PROXY")

    root_domain = require_config_value("ROOT_DOMAIN")

    require_dir(
        f"/etc/letsencrypt/live/{root_domain}",
        "Letsencrypt SSL certificates directory",
    )

    copy_nginx_config()

    print_step(f"Creating nginx log directory at {NGINX_LOG_DIR}...")
    ensure_dir(NGINX_LOG_DIR)

    ensure_network()

    run_container(
        name="server-proxy",
        opts=[
            "--restart",
            "unless-stopped",
            "--network",
            DOCKER_NETWORK_NAME,
            "--ip",
            NGINX_CONTAINER_IP,
            "-p",
            "80:80",
            "-p",
            "443:443",
            "-p",
            "25565:25565",
            "--read-only",
            "-v",
            f"{NGINX_CONFIG_PATH}/conf/nginx.conf:/etc/nginx/nginx.conf:ro",
            "-v",
            f"{NGINX_CONFIG_PATH}/conf.d:/etc/nginx/conf.d:ro",
            "-v",
            f"{NGINX_CONFIG_PATH}/snippets:/etc/nginx/snippets:ro",
            "-v",
            f"{NGINX_CONFIG_PATH}/sites-enabled:/etc/nginx/sites-enabled:ro",
            "-v",
            f"{NGINX_CONFIG_PATH}/streams-enabled:/etc/nginx/streams-enabled:ro",
            "-v",
            "/etc/letsencrypt:/etc/letsencrypt:ro",
            "-v",
            f"{NGINX_LOG_DIR}:/var/log/nginx:rw",
            "-v",
            f"{NGINX_VAR_DIR}:/var/www:ro",
            "--tmpfs",
            "/var/cache/nginx:rw,noexec,nosuid,size=100m",
            "--tmpfs",
            "/var/run:rw,noexec,nosuid,size=10m",
            "--health-cmd=nginx -t",
            "--health-interval=30s",
            "--health-timeout=3s",
            "--health-retries=3",
            "--health-start-period=30s",
            "nginx:latest",
        ],
        notes=[
            f"Move site configs to {NGINX_CONFIG_PATH}/sites-enabled to enable them",
            "Run nginx-update to pull the latest snippets and conf files",
            "Run nginx-reload to reload the running proxy container",
        ],
    )


if __name__ == "__main__":
    main()
