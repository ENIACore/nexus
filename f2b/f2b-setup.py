#!/usr/bin/env python3

import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import require_dir
from common import ensure_dir, run_cmd, write_lines
from config import F2B_CONFIG_PATH
from formatting import print_header, print_info, print_step, print_success

NGINX_LOG_DIR = "/var/log/nginx"
F2B_JAIL_SRC = F2B_CONFIG_PATH / "jail.local"
F2B_JAIL_DEST = "/etc/fail2ban/jail.local"


def install_fail2ban() -> None:
    result = run_cmd("dpkg -s fail2ban", capture_output=True)
    if result.returncode == 0:
        print_info("fail2ban already installed, skipping")
        return
    print_step("Installing fail2ban...")
    run_cmd("sudo apt update && sudo apt install fail2ban -y")


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

    require_dir(NGINX_LOG_DIR, "Nginx log directory for fail2ban monitoring")

    install_fail2ban()

    ensure_dir(str(F2B_CONFIG_PATH))

    generate_jail_local()

    print_step(f"Symlinking {F2B_JAIL_SRC} -> {F2B_JAIL_DEST}...")
    run_cmd(f"sudo ln -sf {F2B_JAIL_SRC} {F2B_JAIL_DEST}")

    print_step("Restarting and enabling fail2ban...")
    run_cmd("sudo systemctl restart fail2ban")
    run_cmd("sudo systemctl enable fail2ban")

    print_success("fail2ban configured successfully")
    print_info("")
    print_info("Next steps:")
    print_info(f"  - Check active jails: sudo fail2ban-client status")
    print_info(f"  - Edit config:        {F2B_JAIL_SRC}")
    print_info(f"  - Reload changes:     sudo systemctl reload fail2ban")


if __name__ == "__main__":
    main()
