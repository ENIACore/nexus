#!/bin/bash

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)
SCRIPT_FILE="${BASE_DIR}/cloudflare/update_dns.sh"
CRON_SCHEDULE="*/5 * * * *"

if crontab -l 2>/dev/null | grep -q "update_dns"; then
    echo "Cron job entry already exists"
    exit 1
fi

(crontab -l 2>/dev/null; echo "@reboot ${SCRIPT_FILE}") | crontab -
(crontab -l 2>/dev/null; echo "${CRON_SCHEDULE} ${SCRIPT_FILE}") | crontab -
