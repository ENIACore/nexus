#!/usr/bin/env python3

import json
import re
import subprocess
import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import require_dir
from config import prompt_and_save, require_config_value
from formatting import (
    get_input,
    print_error,
    print_header,
    print_info,
    print_step,
    print_success,
    print_warning,
)

QBIT_CONTAINER_NAME = "qbittorrent"
JACKETT_CONTAINER_NAME = "jackett"
JACKETT_URL = "http://jackett.internal:9117"
JACKETT_CONFIG_PATH_IN_QBIT = "/config/data/nova3/engines/jackett.json"
JACKETT_API_KEY_PATTERN = re.compile(r"^[a-zA-Z0-9]{32}$")


def _container_running(name: str) -> bool:
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
    )
    return name in result.stdout.splitlines()


def _docker_exec(
    container: str, cmd: list[str], stdin: str | None = None
) -> subprocess.CompletedProcess:
    args = ["docker", "exec"]
    if stdin is not None:
        args.append("-i")
    args.append(container)
    args.extend(cmd)
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        input=stdin,
    )


def check_containers() -> None:
    print_step("Checking qBittorrent container status...")
    if not _container_running(QBIT_CONTAINER_NAME):
        print_error(
            f"qBittorrent container '{QBIT_CONTAINER_NAME}' is not running"
        )
        print_error("Start it before running this script")
        sys.exit(1)
    print_success("qBittorrent container is running")

    if not _container_running(JACKETT_CONTAINER_NAME):
        print_warning(
            "Jackett container is not running — config will be written, "
            "but searches will fail until it is started"
        )


def prompt_api_key() -> str:
    while True:
        api_key = prompt_and_save(
            "JACKETT_API_KEY",
            "Enter Jackett API key (from the top-right of the Jackett web UI)",
            secret=True,
        )

        if JACKETT_API_KEY_PATTERN.match(api_key):
            return api_key

        print_warning(
            "API key doesn't look like a standard 32-character Jackett key"
        )
        confirm = get_input("Use it anyway? (y/N)", default="n")
        if confirm.lower() == "y":
            return api_key


def write_jackett_config(api_key: str) -> None:
    config = {
        "api_key": api_key,
        "url": JACKETT_URL,
        "tracker_first": False,
        "thread_count": 20,
    }
    config_json = json.dumps(config, indent=4)
    engines_dir = JACKETT_CONFIG_PATH_IN_QBIT.rsplit("/", 1)[0]

    print_step(
        "Ensuring plugin engines directory exists in qBittorrent container..."
    )
    result = _docker_exec(QBIT_CONTAINER_NAME, ["mkdir", "-p", engines_dir])
    if result.returncode != 0:
        print_error("Failed to create engines directory inside container")
        sys.exit(1)

    print_step("Writing jackett.json into qBittorrent container...")
    result = _docker_exec(
        QBIT_CONTAINER_NAME,
        [
            "sh",
            "-c",
            f"cat > '{JACKETT_CONFIG_PATH_IN_QBIT}' "
            f"&& chown 1000:1000 '{JACKETT_CONFIG_PATH_IN_QBIT}' "
            f"&& chmod 644 '{JACKETT_CONFIG_PATH_IN_QBIT}'",
        ],
        stdin=config_json,
    )
    if result.returncode != 0:
        print_error("Failed to write jackett.json to container")
        sys.exit(1)
    print_success(f"Wrote {JACKETT_CONFIG_PATH_IN_QBIT}")


def verify_config() -> None:
    print_step("Verifying configuration...")
    result = _docker_exec(
        QBIT_CONTAINER_NAME, ["cat", JACKETT_CONFIG_PATH_IN_QBIT]
    )
    if result.returncode != 0:
        print_error("Could not read back configuration file")
        sys.exit(1)
    print_success("Configuration file verified in container")


def test_connectivity() -> None:
    print_step("Testing connectivity from qBittorrent to Jackett...")

    wget_result = _docker_exec(
        QBIT_CONTAINER_NAME,
        [
            "sh",
            "-c",
            f"command -v wget >/dev/null && wget -qO- --timeout=5 {JACKETT_URL} >/dev/null",
        ],
    )
    if wget_result.returncode == 0:
        print_success(f"qBittorrent can reach Jackett at {JACKETT_URL}")
        return

    curl_result = _docker_exec(
        QBIT_CONTAINER_NAME,
        [
            "sh",
            "-c",
            f"command -v curl >/dev/null && curl -sf --max-time 5 {JACKETT_URL} >/dev/null",
        ],
    )
    if curl_result.returncode == 0:
        print_success(f"qBittorrent can reach Jackett at {JACKETT_URL}")
        return

    print_warning(
        "Could not verify connectivity to Jackett "
        "(wget/curl unavailable, or VPN may be blocking inter-container traffic)"
    )
    print_warning(
        f"If searches fail, check that the qBittorrent VPN config allows access to {JACKETT_URL}"
    )


def main():
    print_header("SETTING UP JACKETT/QBITTORRENT SEARCH PLUGIN CONFIG")

    media_path = require_config_value("MEDIA_SERVICES_PATH")
    require_dir(media_path, "Media services path")

    check_containers()

    api_key = prompt_api_key()

    write_jackett_config(api_key)

    verify_config()

    test_connectivity()

    print_info("")
    print_info("Next steps:")
    print_info("1. Open the qBittorrent WebUI and go to the Search tab")
    print_info("2. Click 'Search plugins...' and confirm Jackett is enabled")
    print_info(
        "3. Run a test search to verify results come back from Jackett"
    )


if __name__ == "__main__":
    main()
