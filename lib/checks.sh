#!/bin/bash

source "/opt/nexus/lib/print.sh"
source "/etc/nexus/conf/conf.sh"

# Ensure nexus user exists, creating it if necessary
ensure_nexus_user() {
    if id "${NEXUS_USER}" &>/dev/null; then
        print_info "Validated system user '${NEXUS_USER}' exists"
        return 0
    fi

    print_info "System user '${NEXUS_USER}' does not exist, creating..."

    sudo useradd \
        --system \
        --no-create-home \
        --shell /usr/sbin/nologin \
        --comment "Nexus service user" \
        "${NEXUS_USER}"

    if [[ $? -eq 0 ]]; then
        print_success "System user '${NEXUS_USER}' created"
        return 0
    else
        print_error "Failed to create user '${NEXUS_USER}'"
        exit 1
    fi
}

# Check if nexus user exists, exit with error if not
require_nexus_user() {
    if ! id "${NEXUS_USER}" &>/dev/null; then
        print_error "ERROR: System user '${NEXUS_USER}' does not exist"
        print_error "Run scripts/create_nexus_user.sh to create it"
        exit 1
    fi
}
