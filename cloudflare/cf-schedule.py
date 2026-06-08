#!/usr/bin/env python3

import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import require_server_user
from common import run_cmd, write_lines
from config import SERVER_USER, require_config_value
from formatting import print_header, print_step, print_success

CF_CRON_FILE = "/etc/cron.d/cloudflare-dns"
CF_CRON_SCHEDULE = "*/5 * * * *"
CF_DNS_SCRIPT = "/usr/local/sbin/cf-update-dns"


def main():
    print_header("SCHEDULING DNS UPDATE JOB")

    require_config_value("CF_API_KEY")
    require_server_user()

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
            f"@reboot root {CF_DNS_SCRIPT} >> /var/log/cloudflare/cron.log 2>&1",
            f"",
            f"# Run every 5 minutes",
            f"{CF_CRON_SCHEDULE} root {CF_DNS_SCRIPT} >> /var/log/cloudflare/cron.log 2>&1",
        ],
    )

    run_cmd(f"sudo chmod 644 {CF_CRON_FILE}")

    print_success(f"Cron job created at {CF_CRON_FILE}")
    print_success(
        f"DNS update will run every 5 minutes as user '{SERVER_USER}'"
    )


if __name__ == "__main__":
    main()
