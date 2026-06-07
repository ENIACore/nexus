#!/usr/bin/env python3
# Requirement check functions for server-configs - /usr/local/sbin/_lib/checks.py

import pwd
import subprocess
import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from formatting import print_error, print_info, print_success

SERVER_USER: str = "server"


def _user_exists(username: str) -> bool:
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False


def ensure_server_user() -> None:
    """Ensure server user exists, creating it if necessary."""
    if _user_exists(SERVER_USER):
        print_info(f"Validated system user '{SERVER_USER}' exists")
        return

    print_info(f"System user '{SERVER_USER}' does not exist, creating...")

    result = subprocess.run(
        [
            "sudo",
            "useradd",
            "--system",
            "--no-create-home",
            "--shell",
            "/usr/sbin/nologin",
            "--comment",
            "Server service user",
            SERVER_USER,
        ],
    )

    if result.returncode == 0:
        print_success(f"System user '{SERVER_USER}' created")
    else:
        print_error(f"Failed to create user '{SERVER_USER}'")
        sys.exit(1)


def require_server_user() -> None:
    """Check if server user exists, exit with error if not."""
    if not _user_exists(SERVER_USER):
        print_error(f"ERROR: System user '{SERVER_USER}' does not exist")
        print_error("Run scripts/create_server_user.py to create it")
        sys.exit(1)


def require_file(file_path: str, description: str = "") -> None:
    """Validate that a file exists, exit with error if not."""
    from pathlib import Path

    desc = description or file_path
    if not Path(file_path).is_file():
        print_error(f"Required file not found: {desc}")
        print_error(f"Path: {file_path}")
        sys.exit(1)


def require_dir(dir_path: str, description: str = "") -> None:
    """Validate that a directory exists, exit with error if not."""
    from pathlib import Path

    desc = description or dir_path
    if not Path(dir_path).is_dir():
        print_error(f"Required directory not found: {desc}")
        print_error(f"Path: {dir_path}")
        sys.exit(1)
