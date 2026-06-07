#!/usr/bin/env python3

import subprocess
import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from formatting import print_error, print_info, print_step, print_success

NETWORK_NAME: str = "server-net"
NETWORK_SUBNET: str = "172.18.0.0/16"
NETWORK_GATEWAY: str = "172.18.0.1"
from formatting import (
    GREY,
    RESET,
    YELLOW,
    print_error,
    print_group_end,
    print_group_start,
    print_group_step,
    print_info,
    print_step,
    print_success,
)


def ensure_network() -> None:
    """Ensure the Docker network exists, creating it if necessary."""
    probe = subprocess.run(
        ["docker", "network", "inspect", NETWORK_NAME],
        capture_output=True,
    )

    if probe.returncode == 0:
        print_info(f"Validated Docker network '{NETWORK_NAME}' exists")
        return

    print_step(f"Creating Docker network '{NETWORK_NAME}'")

    result = subprocess.run(
        [
            "docker",
            "network",
            "create",
            "--driver",
            "bridge",
            "--subnet",
            NETWORK_SUBNET,
            "--gateway",
            NETWORK_GATEWAY,
            NETWORK_NAME,
        ],
        capture_output=True,
    )

    if result.returncode == 0:
        print_success(f"Docker network '{NETWORK_NAME}' created")
    else:
        print_error(
            f"Failed to create Docker network '{NETWORK_NAME}' "
            "(subnet or gateway already in use, choose a new range)"
        )
        sys.exit(1)


def run_container(name: str, opts: list[str], notes: list[str] | None = None) -> None:
    """Run a Docker container and print result.

    Args:
        name:  Container name (passed as --name and used in output).
        opts:  All additional docker run args (volumes, network, restart, image, etc.).
               Do not include 'docker', 'run', '-d', or '--name'.
        notes: Optional list of follow-up info lines printed on success.
    """
    print_group_start(f"Starting container '{name}'")

    cmd = ["docker", "run", "-d", "--name", name, *opts]
    print_group_step(f"Running: {GREY}{' '.join(cmd)}{RESET}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print_group_end(f"Container '{name}' started successfully", success=True)
        if notes:
            print_info("")
            print_info("Next steps:")
            for i, note in enumerate(notes, start=1):
                print_info(f"{YELLOW}{i}. {note}{RESET}")
    else:
        err = result.stderr.strip()
        print_group_step(err)
        print_group_end(f"Failed to start container '{name}'", success=False)
        sys.exit(1)
