#!/usr/bin/env python3

"""
Server Installation Script
"""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "bin" / "_lib"))
from common import copy_path, run_cmd  # noqa: E402
from formatting import (  # noqa: E402
    RED,
    RESET,
    print_group_end,
    print_group_start,
    print_group_step,
    print_step,
    print_success,
    print_warning,
)

REPO_URL = "https://github.com/ENIACore/server-configs.git"
CLONE_PATH = Path("/tmp/srvr-install")


def clone_repository() -> Path:
    print_step("Cloning nexus repository...")

    # Remove existing clone if present
    if CLONE_PATH.exists():
        shutil.rmtree(CLONE_PATH)

    run_cmd(f"git clone {REPO_URL} {CLONE_PATH}", True)
    print_success(f"Repository cloned to {CLONE_PATH}")

    return CLONE_PATH


def create_directories() -> None:
    print_step("Creating system directories...")

    directories = [
        "/etc/cloudflare",
        "/etc/nginx",
        "/etc/f2b",
        "/etc/ufw",
        "/etc/jelly",
        "/etc/jfa",
        "/etc/nextcloud",
        "/etc/jackett",
        "/etc/vault",
        "/etc/raid",
        "/etc/server",
        "/etc/mc",
    ]

    print_group_start("Creating configuration directories")
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print_group_step(f"Created directory: {directory}")
        except Exception as e:
            print_group_end(
                f"Failed to create directory {directory}: {e}", success=False
            )
            sys.exit(1)
    print_group_end()


def copy_template_files():
    print_step("Copying template files to /etc/<service>/<file>.template...")

    keys_path = CLONE_PATH / "keys"
    templates = [
        ("/etc/cloudflare", "cloudflare.toml.template"),
        ("/etc/server", "mlm.toml.template"),
        ("/etc/server-site", "personal-site.toml.template"),
        ("/etc/server", "wg0.conf.template"),
    ]

    print_group_start("Copying template files")
    for template in templates:
        src = keys_path / template[1]
        dest = Path(template[0]) / template[1]
        copy_path(src, dest)
        print_group_step(f"Copied template file {template[1]} to {src}")
    print_group_end(
        f"{RED} Make sure to fill in values and remove .template tag for all template files{RESET}"
    )


def cleanup():
    print_step("Cleaning up temporary files...")

    if CLONE_PATH.exists():
        try:
            shutil.rmtree(CLONE_PATH)
            print_success(f"Removed temporary directory {CLONE_PATH}")
        except Exception:
            print_warning(f"Failed to remove {CLONE_PATH}")


def create_config():
    print_step("Getting values for server configuration")


# Nexus domain and subdomains
# export NEXUS_DOMAIN="{domain}"
# export NEXUS_WILDCARD_DOMAIN="*.{domain}"
# export NEXUS_JELLY_SUBDOMAIN="jelly.{domain}"
# export NEXUS_QBIT_SUBDOMAIN="qbit.{domain}"
# export NEXUS_VAULT_SUBDOMAIN="vault.{domain}"
# export NEXUS_NEXTCLOUD_SUBDOMAIN="nextcloud.{domain}"

# Nexus service user
# export NEXUS_USER=nexus

# Nexus main log dir
# export NEXUS_LOG_DIR="/var/log/nexus"

# Nexus main opt and etc dir
# export NEXUS_OPT_DIR="/opt/nexus"
# export NEXUS_ETC_DIR="/etc/nexus"

# export NEXUS_ESSENTIAL_SERVICES_PATH="{essential_services_path}"
# export NEXUS_CORE_SERVICES_PATH="{core_services_path}"
# export NEXUS_MEDIA_SERVICES_PATH="{media_services_path}"
"""

def create_config():
    print_step("Creating configuration file...")

    # Get domain from user
    domain = input(f"{Colors.CYAN}Enter your root domain (e.g., example.com): {Colors.RESET}").strip()

    if not domain:
        print_error("Domain cannot be empty")
        sys.exit(1)

    # Get path for essential services (vaultwarden, backups etc) 
    essential_services_path = input(f"{Colors.CYAN}Enter the path for all essential services (e.g., /mnt/essential): {Colors.RESET}").strip()
    if not essential_services_path:
        print_error("core services path cannot be empty")
        sys.exit(1)

    # Get path for core services (nextcloud, minecraft, etc) 
    core_services_path = input(f"{Colors.CYAN}Enter the path for all core services (e.g., /mnt/core): {Colors.RESET}").strip()
    if not core_services_path:
        print_error("core services path cannot be empty")
        sys.exit(1)

    # Get path for media services (qbittorrent, jellyfin)
    media_services_path = input(f"{Colors.CYAN}Enter the path for all media services (e.g., /mnt/media): {Colors.RESET}").strip()
    if not media_services_path:
        print_error("media services path cannot be empty")
        sys.exit(1)

    # Create config directory
    config_dir = Path("/etc/nexus/conf")
    config_dir.mkdir(parents=True, exist_ok=True)

    # Create config file content
    config_content = f"""  #!/bin/bash
# Nexus Configuration File - /etc/nexus/conf/conf.sh

"""
    # Write config file
    config_file = config_dir / "conf.sh"
    config_file.write_text(config_content)
    config_file.chmod(0o755)

    print_success(f"Configuration file created at {config_file}")
    print_info(f"Root domain: {domain}")
    print_info(f"Essential services path: {essential_services_path}")
    print_info(f"Core services path: {core_services_path}")
    print_info(f"Media services path: {media_services_path}")


if __name__ == "__main__":
    print_header("NEXUS SERVER INSTALLATION")
    
    # Check if running as root
    if os.geteuid() != 0:
        print_error("This script must be run as root")
        sys.exit(1)
    
    create_directories()
    repo_path = clone_repository()
    copy_repo_path(repo_path)
    copy_template_files(repo_path)
    create_config()
    cleanup_temp_files()

    print_success("Initial setup complete!")
"""
