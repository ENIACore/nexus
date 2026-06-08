#!/usr/bin/env python3

"""
Server Setup Script
"""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "bin" / "_lib"))
from common import copy_path, ensure_dir, write_lines
from config import (
    CF_CONFIG_PATH,
    F2B_CONFIG_PATH,
    JACKETT_CONFIG_PATH,
    JELLY_CONFIG_PATH,
    JFA_CONFIG_PATH,
    MC_CONFIG_PATH,
    NEXTCLOUD_CONFIG_PATH,
    NGINX_CONFIG_PATH,
    QBIT_CONFIG_PATH,
    RAID_CONFIG_PATH,
    SERVER_CLONE_PATH,
    SERVER_CONFIG_PATH,
    SERVER_USER,
    UFW_CONFIG_PATH,
    VAULT_CONFIG_PATH,
    get_config_value,
    prompt_and_save,
    require_config_value,
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
        CF_CONFIG_PATH,
        NGINX_CONFIG_PATH,
        F2B_CONFIG_PATH,
        UFW_CONFIG_PATH,
        JELLY_CONFIG_PATH,
        JFA_CONFIG_PATH,
        NEXTCLOUD_CONFIG_PATH,
        JACKETT_CONFIG_PATH,
        VAULT_CONFIG_PATH,
        RAID_CONFIG_PATH,
        MC_CONFIG_PATH,
        SERVER_CONFIG_PATH,
        QBIT_CONFIG_PATH,
    ]

    print_step("Creating configuration directories")
    for directory in directories:
        ensure_dir(str(directory))
    print_group_end()


def copy_template_files():
    print_step("Copying template files to /etc/<service>/<file>.template...")

    keys_path = SERVER_CLONE_PATH / "keys"
    templates = [
        (SERVER_CONFIG_PATH, "mlm.toml.template"),
        (QBIT_CONFIG_PATH, "wg0.conf.template"),
    ]

    print_group_start("Copying template files")
    for template in templates:
        src = keys_path / template[1]
        dest = Path(template[0]) / template[1]
        copy_path(src, dest)
        print_group_step(f"Copied template file {template[1]} to {dest}")
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
    set_config_value("CORE_SERVICES_PATH", "/mnt/core")

    print_info(f"Setting essential media path (/mnt/media)")
    print_info(
        f"Media services are services used for media hosting (qbittorrent, jellyfin, jackett)"
    )
    set_config_value("MEDIA_SERVICES_PATH", "/mnt/media")

    prompt_and_save(
        "CF_API_KEY",
        "Enter the Cloudflare Bearer API token for DNS updates",
        secret=True,
    )

    print_info(f"Setting CF_CONFIG_PATH ({CF_CONFIG_PATH})")
    set_config_value("CF_CONFIG_PATH", str(CF_CONFIG_PATH))
    print_info(f"Setting NGINX_CONFIG_PATH ({NGINX_CONFIG_PATH})")
    set_config_value("NGINX_CONFIG_PATH", str(NGINX_CONFIG_PATH))
    print_info(f"Setting F2B_CONFIG_PATH ({F2B_CONFIG_PATH})")
    set_config_value("F2B_CONFIG_PATH", str(F2B_CONFIG_PATH))
    print_info(f"Setting UFW_CONFIG_PATH ({UFW_CONFIG_PATH})")
    set_config_value("UFW_CONFIG_PATH", str(UFW_CONFIG_PATH))
    print_info(f"Setting JELLY_CONFIG_PATH ({JELLY_CONFIG_PATH})")
    set_config_value("JELLY_CONFIG_PATH", str(JELLY_CONFIG_PATH))
    print_info(f"Setting JFA_CONFIG_PATH ({JFA_CONFIG_PATH})")
    set_config_value("JFA_CONFIG_PATH", str(JFA_CONFIG_PATH))
    print_info(f"Setting NEXTCLOUD_CONFIG_PATH ({NEXTCLOUD_CONFIG_PATH})")
    set_config_value("NEXTCLOUD_CONFIG_PATH", str(NEXTCLOUD_CONFIG_PATH))
    print_info(f"Setting JACKETT_CONFIG_PATH ({JACKETT_CONFIG_PATH})")
    set_config_value("JACKETT_CONFIG_PATH", str(JACKETT_CONFIG_PATH))
    print_info(f"Setting VAULT_CONFIG_PATH ({VAULT_CONFIG_PATH})")
    set_config_value("VAULT_CONFIG_PATH", str(VAULT_CONFIG_PATH))
    print_info(f"Setting RAID_CONFIG_PATH ({RAID_CONFIG_PATH})")
    set_config_value("RAID_CONFIG_PATH", str(RAID_CONFIG_PATH))
    print_info(f"Setting MC_CONFIG_PATH ({MC_CONFIG_PATH})")
    set_config_value("MC_CONFIG_PATH", str(MC_CONFIG_PATH))
    print_info(f"Setting SERVER_CONFIG_PATH ({SERVER_CONFIG_PATH})")
    set_config_value("SERVER_CONFIG_PATH", str(SERVER_CONFIG_PATH))


def process_templates(root_domain: str) -> None:
    """
    Substitutes domain into template files and moves them to /etc/nginx/sites-available for future use
    """
    template_dir = SERVER_CLONE_PATH / "nginx/templates"
    sites_available = NGINX_CONFIG_PATH / "sites-available"

    ensure_dir(str(sites_available))

    for template in template_dir.glob("*.template"):
        dest_name = template.name.replace(".template", "")
        dest = sites_available / dest_name
        text = template.read_text().replace("${DOMAIN}", root_domain)
        write_lines(dest, text.splitlines())
        print_success(f"Processed template: {template.name} → {dest_name}")


def copy_nginx_config() -> None:
    """
    Copies all relevant nginx config files into /etc/nginx for future use
    """
    nginx_src_path = SERVER_CLONE_PATH / "nginx"

    print_step(f"Copying nginx configuration to {NGINX_CONFIG_PATH}...")
    for subdir in ["conf", "conf.d", "snippets", "streams-available"]:
        copy_path(nginx_src_path / subdir, NGINX_CONFIG_PATH / subdir)

    for subdir in ["sites-enabled", "streams-enabled"]:
        print_step(f"Creating {NGINX_CONFIG_PATH / subdir}...")
        ensure_dir(str(NGINX_CONFIG_PATH / subdir))


def cleanup():
    print_step("Cleaning up temporary files...")

    if SERVER_CLONE_PATH.exists():
        try:
            shutil.rmtree(SERVER_CLONE_PATH)
            print_success(f"Removed temporary directory {SERVER_CLONE_PATH}")
        except Exception:
            print_warning(f"Failed to remove {SERVER_CLONE_PATH}")

    # Remove self and original install script path
    script_path = Path(__file__).resolve()
    try:
        script_path.unlink(missing_ok=True)
        print_success(f"Removed setup script {script_path}")
    except Exception:
        print_warning(f"Failed to remove setup script {script_path}")

    script_path = Path("/tmp/server-install.py")
    try:
        script_path.unlink(missing_ok=True)
        print_success(f"Removed installer script {script_path}")
    except Exception:
        print_warning(f"Failed to remove installer script {script_path}")


if __name__ == "__main__":
    create_directories()
    copy_template_files()
    create_config()
    root_domain = require_config_value("ROOT_DOMAIN")
    process_templates(root_domain)
    copy_nginx_config()
    cleanup()
