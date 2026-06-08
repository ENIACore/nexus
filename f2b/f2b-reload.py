#!/usr/bin/env python3

import subprocess
import sys
import time

sys.path.insert(0, "/usr/local/sbin/_lib")
from checks import require_file
from common import run_cmd
from config import F2B_CONFIG_PATH
from formatting import print_error, print_header, print_step, print_success

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


def main():
    print_header("RELOADING FAIL2BAN")

    require_file(str(F2B_JAIL_SRC), "fail2ban configuration file")

    print_step("Ensuring symlink to system fail2ban configuration")
    run_cmd(f"sudo ln -sf {F2B_JAIL_SRC} {F2B_JAIL_DEST}")

    print_step("Restarting fail2ban service")
    run_cmd("sudo systemctl restart fail2ban")

    print_success("fail2ban reloaded successfully")

    print_step("Waiting for fail2ban to be ready...")
    if wait_for_fail2ban():
        run_cmd("sudo fail2ban-client status")
    else:
        print_error("fail2ban started but socket not ready after 10 seconds")
        sys.exit(1)


if __name__ == "__main__":
    main()
