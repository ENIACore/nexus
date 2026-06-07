#!/bin/bash
#!/bin/bash
# Creates personal site (Next.JS + payload CMS)

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

print_header "SETTING UP PERSONAL SITE"

# Ensure connection string with password is available
require_file "${NEXUS_ETC_DIR}/keys/postgres.sh" "Postgres secrets file"
# Ensure payload secrets are available
require_file "${NEXUS_ETC_DIR}/keys/personal_site.sh" "Personal site secrets file"

# Source the secrets files
source "${NEXUS_ETC_DIR}/keys/postgres.sh"
source "${NEXUS_ETC_DIR}/keys/personal_site.sh"

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

docker pull eniacore/personal-site:latest

print_info "Starting site container..."
sudo docker run --name nexus-personal-site \
    --network nexus-net \
    -e PAYLOAD_SECRET="${NEXUS_PERSONAL_SITE_SECRET}" \
    -e DATABASE_URL="${NEXUS_PG_CONN_STR}" \
    -v nexus-personal-site-media:/app/media \
    -d eniacore/personal-site:latest
