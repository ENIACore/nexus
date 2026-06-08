#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

sys.path.insert(0, "/usr/local/sbin/_lib")
from common import run_cmd
from config import NGINX_CONFIG_PATH
from formatting import (
    print_error,
    print_header,
    print_info,
    print_step,
    print_success,
)

ENABLED_DIRS = [
    NGINX_CONFIG_PATH / "sites-enabled",
    NGINX_CONFIG_PATH / "streams-enabled",
]


def find_enabled(site_name: str) -> Path:
    """Find sitename.conf in sites-enabled or streams-enabled.
    Returns the path or exits with error."""
    filename = f"{site_name}.conf"

    for enabled_dir in ENABLED_DIRS:
        candidate = enabled_dir / filename
        if candidate.exists() or candidate.is_symlink():
            print_info(f"Found {filename} in {enabled_dir.name}")
            return candidate

    print_error(
        f"Config '{filename}' not found in sites-enabled or streams-enabled"
    )
    sys.exit(1)


def main():
    print_header("DISABLING NGINX SITE")

    parser = argparse.ArgumentParser()
    parser.add_argument("site", help="Site name (without .conf)")
    args = parser.parse_args()

    target = find_enabled(args.site)

    print_step(f"Disabling {target.name}...")
    target.unlink()
    print_success(f"Removed {target}")

    run_cmd(f"{sys.executable} /usr/local/sbin/nginx-reload")


if __name__ == "__main__":
    main()
