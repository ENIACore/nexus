#!/usr/bin/env python3

import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from common import ensure_dir, run_cmd
from config import UFW_CONFIG_PATH
from formatting import (
    print_header,
    print_info,
    print_step,
    print_success,
    print_warning,
)

BLOCKLIST_URL = "https://gist.githubusercontent.com/arter97/2b71e193700ab002c75d1e5a0e7da6dc/raw/firewall.sh"
BLOCKLIST_SCRIPT = UFW_CONFIG_PATH / "blocklist.sh"

UFW_RULES = [
    ("22/tcp", "OpenSSH"),
    ("80/tcp", "HTTP"),
    ("443/tcp", "HTTPS"),
    ("25565/tcp", "Minecraft"),
]


def install_packages() -> None:
    print_step("Installing required packages...")
    run_cmd("sudo apt install iptables ipset ufw cron curl wget rsyslog -y")


def configure_ufw() -> None:
    print_step("Configuring UFW rules...")
    run_cmd("sudo ufw --force reset")
    run_cmd("sudo ufw default deny incoming")
    run_cmd("sudo ufw default allow outgoing")

    print_step("Allowing SSH, HTTP, HTTPS, and Minecraft...")
    for port, comment in UFW_RULES:
        run_cmd(f"sudo ufw allow {port} comment '{comment}'")


def setup_blocklist() -> None:
    print_step("Downloading IP blocklist updater...")
    run_cmd(f"sudo wget -q {BLOCKLIST_URL} -O {BLOCKLIST_SCRIPT}")
    run_cmd(f"sudo chmod 755 {BLOCKLIST_SCRIPT}")

    print_step("Running initial IP blocklist update...")
    import subprocess

    result = subprocess.run(
        ["sudo", str(BLOCKLIST_SCRIPT)], capture_output=True
    )
    if result.returncode == 0:
        print_info("IP blocklist updated successfully")
    else:
        print_warning("Failed to update IP blocklist, continuing anyway")


def enable_ufw() -> None:
    print_step("Enabling UFW firewall...")
    run_cmd("sudo ufw --force enable")
    print_success("UFW firewall configured and enabled successfully")


def main():
    print_header("CONFIGURING UFW FIREWALL FOR SERVER")

    install_packages()

    print_step(
        f"Creating UFW configuration directory at {UFW_CONFIG_PATH}..."
    )
    ensure_dir(str(UFW_CONFIG_PATH))

    configure_ufw()
    setup_blocklist()
    enable_ufw()

    print_info("")
    print_info("Next steps:")
    print_info("1. Run ufw-schedule to set up automatic blocklist updates")
    print_info("2. Use 'sudo ufw status' to view current firewall rules")
    print_info("3. Run ufw-update to manually update the IP blocklist")


if __name__ == "__main__":
    main()
