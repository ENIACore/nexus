#!/bin/bash

source "/opt/nexus/lib/print.sh"
source "/etc/nexus/conf/conf.sh"

# Check if nexus user exists, exit with error if not
require_nexus_user() {
    if ! id "${NEXUS_USER}" &>/dev/null; then
        print_error "ERROR: System user '${NEXUS_USER}' does not exist"
        print_error "Run scripts/create_nexus_user.sh to create it"
        exit 1
    fi
}
