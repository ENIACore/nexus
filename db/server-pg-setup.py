#!/usr/bin/env python3

import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import require_server_user
from config import DOCKER_NETWORK_NAME, prompt_and_save, require_config_value
from docker import ensure_network, run_container
from formatting import print_header, print_success

PG_CONTAINER_NAME = "nexus-pg"
PG_IMAGE = "postgres:latest"
PG_DATA_VOLUME = "nexus-pg-data"
PG_DATA_PATH = "/var/lib/postgresql/data"


def main():
    print_header("SETTING UP POSTGRES DATABASE")

    require_server_user()

    prompt_and_save(
        "PG_PASSWORD",
        "Enter the PostgreSQL superuser password",
        secret=True,
    )
    pg_password = require_config_value("PG_PASSWORD")

    ensure_network()

    run_container(
        name=PG_CONTAINER_NAME,
        opts=[
            "--network",
            DOCKER_NETWORK_NAME,
            "-e",
            f"POSTGRES_PASSWORD={pg_password}",
            "-v",
            f"{PG_DATA_VOLUME}:{PG_DATA_PATH}",
            "--restart",
            "unless-stopped",
            PG_IMAGE,
        ],
        notes=[
            f"PostgreSQL is available to containers on '{DOCKER_NETWORK_NAME}' at port 5432",
            f"Data is persisted in Docker volume '{PG_DATA_VOLUME}'",
        ],
    )

    print_success("Postgres setup complete")


if __name__ == "__main__":
    main()
