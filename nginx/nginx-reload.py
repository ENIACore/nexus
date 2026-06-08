#!/usr/bin/env python3

import subprocess
import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from formatting import print_error, print_header, print_success

NGINX_CONTAINER_NAME = "server-proxy"


def main():
    print_header("RELOADING NGINX")

    result = subprocess.run(
        ["docker", "exec", NGINX_CONTAINER_NAME, "nginx", "-s", "reload"],
        capture_output=True,
    )
    if result.returncode == 0:
        print_success("Nginx reloaded successfully")
    else:
        print_error("Failed to reload nginx")
        sys.exit(1)


if __name__ == "__main__":
    main()
