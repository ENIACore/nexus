#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/usr/local/sbin/_lib")
from formatting import print_error, print_info, print_success


def prune_docker_system() -> None:
    print_info("Pruning docker containers, volumes, and images...")
    result = subprocess.run(
        ["docker", "system", "prune", "-a", "-f"],
        text=True,
    )
    if result.returncode == 0:
        print_success("Docker system pruned successfully")
    else:
        print_error("Docker system prune failed")
        sys.exit(1)


def main() -> None:
    prune_docker_system()


if __name__ == "__main__":
    main()
