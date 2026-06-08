#!/usr/bin/env python3

import sys

sys.path.insert(0, "/usr/local/sbin/_lib")
from common import run_cmd
from formatting import print_header, print_info

JAILS = [
    "nginx-http-auth",
    "nginx-bad-request",
    "nginx-botsearch",
    "nginx-limit-req",
    "sshd",
]


def main():
    print_header("FAIL2BAN NGINX JAIL STATUS")

    for jail in JAILS:
        run_cmd(f"sudo fail2ban-client status {jail}")
        print_info("")


if __name__ == "__main__":
    main()
