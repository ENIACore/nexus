#!/bin/bash
source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"

print_header "FAIL2BAN NGINX JAIL STATUS"

JAILS=("nginx-http-auth" "nginx-bad-request" "nginx-botsearch" "nginx-limit-req sshd")

for jail in "${JAILS[@]}"; do
    print_step "${jail}"
    sudo fail2ban-client status "${jail}"
    print_info ""
done
