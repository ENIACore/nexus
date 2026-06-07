#!/usr/bin/env python3

"""
Server Setup Script
"""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "bin" / "_lib"))
from common import copy_path
from config import (
    SERVER_CLONE_PATH,
    SERVER_CONFIG_PATH,
    SERVER_USER,
    get_config_value,
    prompt_and_save,
    set_config_value,
)
from formatting import (
    RED,
    RESET,
    print_group_end,
    print_group_start,
    print_group_step,
    print_info,
    print_step,
    print_success,
    print_warning,
)


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
        "/etc/mc",
        SERVER_CONFIG_PATH,
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

    keys_path = SERVER_CLONE_PATH / "keys"
    templates = [
        ("/etc/cloudflare", "cloudflare.toml.template"),
        ("/etc/server", "mlm.toml.template"),
        (SERVER_CONFIG_PATH, "personal-site.toml.template"),
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


def create_config():
    print_step("Getting values for server configuration")
    prompt_and_save(
        "ROOT_DOMAIN", "Enter the root domain for the server including TLD"
    )
    root_domain = get_config_value("ROOT_DOMAIN")

    print_info(f"Setting wildcard domain (*.{root_domain})")
    set_config_value("WILDCARD_DOMAIN", f"*.{root_domain}")

    print_info(f"Setting jellyfin subdomain (jelly.{root_domain})")
    set_config_value("JELLY_SUBDOMAIN", f"jelly.{root_domain}")

    print_info(f"Setting qbittorrent subdomain (qbit.{root_domain})")
    set_config_value("QBIT_SUBDOMAIN", f"qbit.{root_domain}")

    print_info(f"Setting vaultwarden subdomain (vault.{root_domain})")
    set_config_value("VAULT_SUBDOMAIN", f"vault.{root_domain}")

    print_info(f"Setting nextcloud subdomain (nextcloud.{root_domain})")
    set_config_value("NEXTCLOUD_SUBDOMAIN", f"nextcloud.{root_domain}")

    print_info(f"Setting server user ({SERVER_USER})")
    set_config_value("USER", f"{SERVER_USER}")

    print_info(f"Setting essential services path (/mnt/essential)")
    print_info(
        f"Essential services are the most important services used (vaultwarden)"
    )
    set_config_value("ESSENTIAL_SERVICES_PATH", "/mnt/essential")

    print_info(f"Setting essential core path (/mnt/core)")
    print_info(
        f"Core services are services used daily (minecraft, nextcloud)"
    )
    set_config_value("ESSENTIAL_SERVICES_PATH", "/mnt/core")

    print_info(f"Setting essential media path (/mnt/media)")
    print_info(
        f"Media services are services used for media hosting (qbittorrent, jellyfin, jackett)"
    )
    set_config_value("ESSENTIAL_SERVICES_PATH", "/mnt/media")


def cleanup():
    print_step("Cleaning up temporary files...")

    if SERVER_CLONE_PATH.exists():
        try:
            shutil.rmtree(SERVER_CLONE_PATH)
            print_success(f"Removed temporary directory {SERVER_CLONE_PATH}")
        except Exception:
            print_warning(f"Failed to remove {SERVER_CLONE_PATH}")

    script_path = Path(__file__).resolve()
    try:
        script_path.unlink(missing_ok=True)
        print_success(f"Removed installer script {script_path}")
    except Exception:
        print_warning(f"Failed to remove installer script {script_path}")


if __name__ == "__main__":
    create_directories()
    copy_template_files()
    create_config()
    cleanup()
