#!/bin/bash
# User management functions for nexus scripts

NEXUS_USER="nexus"

# Check if nexus user exists, exit with error if not
require_nexus_user() {
    if ! id "${NEXUS_USER}" &>/dev/null; then
        echo "ERROR: System user '${NEXUS_USER}' does not exist"
        echo "Run scripts/create_nexus_user.sh to create it"
        exit 1
    fi
}

# Check if nexus user exists, return 0 if yes, 1 if no
check_nexus_user() {
    if id "${NEXUS_USER}" &>/dev/null; then
        return 0
    else
        return 1
    fi
}
