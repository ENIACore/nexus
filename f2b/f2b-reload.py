#!/usr/bin/env python3

import subprocess
import sys
import time

sys.path.insert(0, "/usr/local/sbin/_lib")
from common import ensure_dir, run_cmd, write_lines
from config import F2B_CONFIG_PATH
from formatting import print_header, print_info, print_step, print_success

NGINX_LOG_DIR = "/var/log/nginx"
NGINX_LOG_PLACEHOLDERS = ["access.log", "error.log"]
F2B_JAIL_SRC = F2B_CONFIG_PATH / "jail.local"
F2B_JAIL_DEST = "/etc/fail2ban/jail.local"
F2B_PING_RETRIES = 10


def wait_for_fail2ban() -> bool:
    """Poll fail2ban-client ping until ready or timeout."""
    for _ in range(F2B_PING_RETRIES):
        result = subprocess.run(
            ["sudo", "fail2ban-client", "ping"],
            capture_output=True,
        )
        if result.returncode == 0:
            return True
        time.sleep(1)
    return False


def install_fail2ban() -> None:
    result = run_cmd("dpkg -s fail2ban", capture_output=True)
    if result.returncode == 0:
        print_info("fail2ban already installed, skipping")
        return
    print_step("Installing fail2ban...")
    run_cmd("sudo apt update && sudo apt install fail2ban -y")


def ensure_nginx_logs() -> None:
    """Touch placeholder nginx log files so fail2ban jails can resolve the logpath glob.
    fail2ban crashes at startup if no files match the logpath pattern."""
    ensure_dir(NGINX_LOG_DIR)
    print_step(f"Ensuring nginx log placeholders exist in {NGINX_LOG_DIR}...")
    for name in NGINX_LOG_PLACEHOLDERS:
        run_cmd(f"sudo touch {NGINX_LOG_DIR}/{name}")


def generate_jail_local() -> None:
    print_step(f"Generating jail.local at {F2B_JAIL_SRC}...")
    write_lines(
        F2B_JAIL_SRC,
        [
            "[DEFAULT]",
            "bantime = 15m",
            "findtime = 15m",
            "maxretry = 5",
            "banaction = ufw",
            "",
            "[sshd]",
            "enabled = true",
            "port = 22",
            "",
            "[nginx-http-auth]",
            "enabled = true",
            "mode = aggressive",
            "backend = auto",
            f"logpath = {NGINX_LOG_DIR}/*.log",
            "",
            "[nginx-bad-request]",
            "enabled = true",
            "backend = auto",
            f"logpath = {NGINX_LOG_DIR}/*.log",
            "",
            "[nginx-botsearch]",
            "enabled = true",
            "backend = auto",
            f"logpath = {NGINX_LOG_DIR}/*.log",
            "",
            "[nginx-limit-req]",
            "enabled = true",
            "backend = auto",
            f"logpath = {NGINX_LOG_DIR}/*.log",
        ],
    )


def main():
    print_header("CONFIGURING FAIL2BAN FOR NGINX")

    install_fail2ban()

    ensure_dir(str(F2B_CONFIG_PATH))

    ensure_nginx_logs()

    generate_jail_local()

    print_step(f"Symlinking {F2B_JAIL_SRC} -> {F2B_JAIL_DEST}...")
    run_cmd(f"sudo ln -sf {F2B_JAIL_SRC} {F2B_JAIL_DEST}")

    print_step("Restarting and enabling fail2ban...")
    run_cmd("sudo systemctl restart fail2ban")
    run_cmd("sudo systemctl enable fail2ban")
    wait_for_fail2ban()

    print_success("fail2ban configured successfully")
    print_info("")
    print_info("Next steps:")
    print_info(f"  - Check active jails: sudo fail2ban-client status")
    print_info(f"  - Edit config:        {F2B_JAIL_SRC}")
    print_info(f"  - Reload changes:     sudo systemctl reload fail2ban")


if __name__ == "__main__":
    main()
