#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import require_server_user
from common import run_cmd, write_lines
from config import SERVER_USER, require_config_value
from formatting import print_error, print_header, print_step, print_success

CF_CRON_FILE = "/etc/cron.d/server-cloudflare-dns"
CF_CRON_SCHEDULE = "*/5 * * * *"
CF_DNS_SCRIPT = "/usr/local/sbin/cf-update-dns"


def main():
    print_header("SCHEDULING DNS UPDATE JOB")

    require_config_value("CF_API_KEY")
    require_server_user()

    if Path(CF_CRON_FILE).exists():
        print_error(f"Cron job already exists at {CF_CRON_FILE}")
        sys.exit(1)

    print_step(f"Creating system cron job at {CF_CRON_FILE}...")

    write_lines(
        CF_CRON_FILE,
        [
            f"# Cloudflare DNS updater - runs as {SERVER_USER} user",
            f"# Updates DNS records every 5 minutes and on reboot",
            f"",
            f"SHELL=/bin/bash",
            f"PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin",
            f"",
            f"# Run on boot",
            f"@reboot {SERVER_USER} {CF_DNS_SCRIPT}",
            f"",
            f"# Run every 5 minutes",
            f"{CF_CRON_SCHEDULE} {SERVER_USER} {CF_DNS_SCRIPT}",
        ],
    )

    run_cmd(f"sudo chmod 644 {CF_CRON_FILE}")

    print_success(f"Cron job created at {CF_CRON_FILE}")
    print_success(
        f"DNS update will run every 5 minutes as user '{SERVER_USER}'"
    )


if __name__ == "__main__":
    main()
