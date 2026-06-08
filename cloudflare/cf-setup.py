#!/usr/bin/env python3

import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import ensure_server_user
from common import ensure_dir, run_cmd, write_lines
from config import (
    CF_CONFIG_PATH,
    SERVER_USER,
    prompt_and_save,
)
from formatting import print_error, print_header, print_step, print_success


def main():
    print_header("SETTING UP CLOUDFLARE DNS AND CRON JOB")

    CF_API_KEY = prompt_and_save(
        "CF_API_KEY",
        "Input API key for cloudflare, no input to keep current value",
        secret=True,
    )
    CF_INI_PATH = CF_CONFIG_PATH / "cloudflare.ini"
    write_lines(CF_INI_PATH, [f"dns_cloudflare_api_token = {CF_API_KEY}"])
    CF_INI_PATH.chmod(0o600)

    CF_LOG_DIR = prompt_and_save(
        "CF_LOG_DIR",
        "Input path to cloudflare log directory, no input for default",
        "/var/log/cloudflare",
    )
    ensure_server_user()

    ensure_dir(CF_LOG_DIR)
    print_step(f"Logs will be written to: {CF_LOG_DIR}/dns.log")

    print_step("Running initial DNS update...")
    """
    result = run_cmd(f"{sys.executable} /usr/local/sbin/cf-update-dns")
    if result.returncode != 0:
        print_error("Initial DNS update failed")
        sys.exit(1)

    print_step("Scheduling automated DNS updates...")
    result = run_cmd(f"{sys.executable} /usr/local/sbin/cf-schedule")
    if result.returncode != 0:
        print_error("Failed to schedule DNS updates")
        sys.exit(1)
    """

    run_cmd(f"sudo chown -R {SERVER_USER}:{SERVER_USER} {CF_LOG_DIR}")
    run_cmd(f"sudo chmod 755 {CF_LOG_DIR}")

    print_success("Cloudflare setup complete")


if __name__ == "__main__":
    main()
