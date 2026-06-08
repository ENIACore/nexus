#!/usr/bin/env python3

import subprocess
import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from formatting import (
    GREEN,
    RED,
    RESET,
    print_error,
    print_header,
    print_info,
    print_warning,
)

NGINX_CONTAINER_NAME = "server-proxy"
NGINX_LOG_DIR = "/var/log/nginx"
NGINX_ACCESS_LOG = f"{NGINX_LOG_DIR}/access.log"
NGINX_ERROR_LOG = f"{NGINX_LOG_DIR}/error.log"
TAIL_LINES = 100


def container_exists() -> bool:
    result = subprocess.run(
        ["docker", "ps", "-a", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
    )
    return NGINX_CONTAINER_NAME in result.stdout.splitlines()


def container_running() -> bool:
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
    )
    return NGINX_CONTAINER_NAME in result.stdout.splitlines()


def logs_exist() -> bool:
    from pathlib import Path

    return Path(NGINX_ACCESS_LOG).exists() or Path(NGINX_ERROR_LOG).exists()


def tail_logs() -> None:
    access_label = f"{GREEN}[ACCESS]{RESET}"
    error_label = f"{RED}[ERROR]{RESET}"

    proc = subprocess.Popen(
        [
            "tail",
            "-f",
            "-n",
            str(TAIL_LINES),
            NGINX_ACCESS_LOG,
            NGINX_ERROR_LOG,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    assert proc.stdout is not None
    try:
        for line in proc.stdout:
            line = line.rstrip()
            if line == f"==> {NGINX_ACCESS_LOG} <==":
                print(f"\n{access_label}")
            elif line == f"==> {NGINX_ERROR_LOG} <==":
                print(f"\n{error_label}")
            else:
                print(line)
    except KeyboardInterrupt:
        proc.terminate()


def main():
    if not container_exists():
        print_error(f"Container '{NGINX_CONTAINER_NAME}' not found")
        sys.exit(1)

    if not container_running():
        print_warning(f"Container '{NGINX_CONTAINER_NAME}' is not running")
        print_info("Showing logs from stopped container...")

    if not logs_exist():
        print_error(f"No log files found in {NGINX_LOG_DIR}")
        sys.exit(1)

    print_header("TAILING NGINX LOGS")
    print_info(f"Log directory: {NGINX_LOG_DIR}")
    print_info("Press Ctrl+C to stop")
    print()

    tail_logs()


if __name__ == "__main__":
    main()
