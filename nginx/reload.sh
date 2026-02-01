#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

if docker exec nexus-proxy nginx -s reload; then
    print_info "Nginx reloaded successfully"
else
    print_error "Failed to reload nginx"
    exit 1
fi
