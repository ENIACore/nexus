#!/usr/bin/env python3
import subprocess
import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from formatting import print_error, print_info, print_success, print_warning


def get_docker_volumes() -> list[str]:
    result = subprocess.run(
        ["docker", "volume", "ls", "-q"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print_error("Failed to list docker volumes")
        print_error(result.stderr.strip())
        sys.exit(1)
    return [v for v in result.stdout.strip().splitlines() if v]


def remove_docker_volumes(volumes: list[str]) -> None:
    result = subprocess.run(
        ["docker", "volume", "rm"] + volumes,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print_success(f"Removed {len(volumes)} volume(s)")
    else:
        print_error("Failed to remove one or more volumes")
        print_error(result.stderr.strip())
        sys.exit(1)


def main() -> None:
    print_info("Fetching docker volumes...")
    volumes = get_docker_volumes()

    if not volumes:
        print_warning("No docker volumes found")
        return

    print_info(f"Found {len(volumes)} volume(s): {', '.join(volumes)}")
    remove_docker_volumes(volumes)


if __name__ == "__main__":
    main()
