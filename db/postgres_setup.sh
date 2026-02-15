#!/bin/bash
# Creates postrgres db for use by nexus services and sites

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

print_header "SETTING UP POSTGRES DATABASE"

# Ensure password is present in secrets file
require_file "${NEXUS_ETC_DIR}/keys/postgres.sh" "Postgres password file containing NEXUS_PG_PASSWORD variable"

# Source the password file
source "${NEXUS_ETC_DIR}/keys/postgres.sh"

# Ensure docker network exists
if ! docker network inspect nexus-net >/dev/null 2>&1; then
    print_step "Creating Docker network 'nexus-net'"

    if ! docker network create \
        --driver bridge \
        --subnet 172.18.0.0/16 \
        --gateway 172.18.0.1 \
        nexus-net >/dev/null 2>&1; then
        print_error "Failed to create Docker network 'nexus-net' (subnet or gateway already in use, choose a new range)"
        exit 1
    fi
fi

# Port 5432 is available to containers on nexus network
print_step "Starting PostgreSQL container..."
sudo docker run --name nexus-pg \
  --network nexus-net \
  -e POSTGRES_PASSWORD="${NEXUS_PG_PASSWORD}" \
  -v nexus-pg-data:/var/lib/postgresql/data \
  -d postgres:latest

if [[ $? -ne 0 ]]; then
    print_error "Failed to start PostgreSQL container"
    exit 1
fi

print_info "PostgreSQL container started successfully"
echo "Postgres setup complete"
