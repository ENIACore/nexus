#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import ensure_server_user
from common import run_cmd
from config import SERVER_USER, require_config_value
from formatting import print_error, print_header, print_info, print_step

CF_CRON_FILE = "/etc/cron.d/server-cloudflare-dns"
CF_CRON_SCHEDULE = "*/5 * * * *"
CF_DNS_SCRIPT = "/usr/local/sbin/cf-update-dns"


def main():
    print_header("SCHEDULING DNS UPDATE JOB")

    require_config_value("CF_API_KEY")
    ensure_server_user()

    if Path(CF_CRON_FILE).exists():
        print_error(f"Cron job already exists at {CF_CRON_FILE}")
        sys.exit(1)

    print_step(f"Creating system cron job at {CF_CRON_FILE}...")

    cron_content = (
        f"# Cloudflare DNS updater - runs as {SERVER_USER} user\n"
        f"# Updates DNS records every 5 minutes and on reboot\n"
        f"\n"
        f"SHELL=/bin/bash\n"
        f"PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin\n"
        f"\n"
        f"# Run on boot\n"
        f"@reboot {SERVER_USER} {CF_DNS_SCRIPT}\n"
        f"\n"
        f"# Run every 5 minutes\n"
        f"{CF_CRON_SCHEDULE} {SERVER_USER} {CF_DNS_SCRIPT}\n"
    )

    subprocess.run(
        ["sudo", "tee", CF_CRON_FILE],
        input=cron_content,
        text=True,
        check=True,
        capture_output=True,
    )
    run_cmd(f"sudo chmod 644 {CF_CRON_FILE}")

    print_info("System cron job created successfully")
    print_info(f"DNS update will run every 5 minutes as user '{SERVER_USER}'")


if __name__ == "__main__":
    main()
