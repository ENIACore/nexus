#!/usr/bin/env python3
import subprocess
import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from formatting import print_error, print_header, print_info, print_success

NGINX_CONTAINER_NAME = "server-proxy"


def test_config() -> bool:
    result = subprocess.run(
        ["docker", "exec", NGINX_CONTAINER_NAME, "nginx", "-t"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print_success("Config test passed")
        return True
    print_error("Config test failed")
    print_error(result.stderr.strip())
    return False


def reload_nginx() -> bool:
    result = subprocess.run(
        ["docker", "exec", NGINX_CONTAINER_NAME, "nginx", "-s", "reload"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print_success("Nginx reloaded successfully")
        return True
    print_error("Failed to reload nginx")
    print_error(result.stderr.strip())
    return False


def print_health() -> None:
    result = subprocess.run(
        [
            "docker",
            "inspect",
            "--format",
            "{{.State.Health.Status}}",
            NGINX_CONTAINER_NAME,
        ],
        capture_output=True,
        text=True,
    )
    status = result.stdout.strip() if result.returncode == 0 else "unknown"
    print_info(f"Container health: {status}")


def main():
    print_header("RELOADING NGINX")

    if not test_config():
        sys.exit(1)

    if not reload_nginx():
        sys.exit(1)

    print_health()


if __name__ == "__main__":
    main()
