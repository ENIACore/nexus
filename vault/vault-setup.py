#!/usr/bin/env python3

import base64
import secrets
import subprocess
import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import ensure_packages, require_dir
from common import ensure_dir
from config import DOCKER_NETWORK_NAME, require_config_value
from docker import ensure_network, run_container
from formatting import (
    print_error,
    print_header,
    print_info,
    print_step,
)

VAULT_ADMIN_PASS_FILE = ".admin_password"


def generate_admin_token() -> tuple[str, str]:
    """Generate a random admin password and its argon2id PHC hash.

    Returns:
        (plaintext_password, argon2id_phc_hash)
    """
    password = base64.b64encode(secrets.token_bytes(36)).decode()
    salt = base64.b64encode(secrets.token_bytes(24)).decode()

    # Bitwarden defaults: m=65540 (64MiB), t=3, p=4
    result = subprocess.run(
        ["argon2", salt, "-e", "-id", "-k", "65540", "-t", "3", "-p", "4"],
        input=password.encode(),
        capture_output=True,
    )

    if result.returncode != 0 or not result.stdout.strip():
        print_error("Failed to generate argon2id PHC string")
        sys.exit(1)

    token = result.stdout.strip().decode()
    return password, token


def save_admin_password(vault_data_dir: str, password: str) -> str:
    from pathlib import Path

    pass_file = Path(vault_data_dir) / VAULT_ADMIN_PASS_FILE
    pass_file.write_text(password + "\n")
    pass_file.chmod(0o600)
    print_info(f"Admin password saved to {pass_file} (keep this safe!)")
    return str(pass_file)


def main():
    print_header("SETTING UP VAULTWARDEN PASSWORD MANAGER")

    essential_path = require_config_value("ESSENTIAL_SERVICES_PATH")
    vault_subdomain = require_config_value("VAULT_SUBDOMAIN")

    require_dir(essential_path, "Essential services path")

    vault_data_dir = f"{essential_path}/vw-data"

    print_step(f"Creating Vaultwarden data directory at {vault_data_dir}...")
    ensure_dir(vault_data_dir)

    ensure_packages(["argon2"])

    print_step("Generating Vaultwarden admin password and argon2id token...")
    admin_password, admin_token = generate_admin_token()
    pass_file = save_admin_password(vault_data_dir, admin_password)

    ensure_network()

    run_container(
        name="vaultwarden",
        opts=[
            "--network",
            DOCKER_NETWORK_NAME,
            "--env",
            f"DOMAIN=https://{vault_subdomain}",
            "--env",
            f"ADMIN_TOKEN={admin_token}",
            "--volume",
            f"{vault_data_dir}:/data/",
            "--restart",
            "unless-stopped",
            "vaultwarden/server:latest",
        ],
        notes=[
            f"Access the admin panel at https://{vault_subdomain}/admin",
            f"Use the password stored in {pass_file} to log in",
            f"Data will be stored in {vault_data_dir}",
        ],
    )


if __name__ == "__main__":
    main()
