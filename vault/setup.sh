#!/bin/bash
source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_VAULT_OPT_DIR="${NEXUS_OPT_DIR}/vault"
NEXUS_VAULT_DATA_DIR="${NEXUS_ESSENTIAL_SERVICES_PATH}/vw-data"

print_header "SETTING UP VAULTWARDEN PASSWORD MANAGER"

# Ensure essential services path exists
require_dir "${NEXUS_ESSENTIAL_SERVICES_PATH}" "Essential services path"

# Create vaultwarden data directory
print_step "Creating Vaultwarden data directory at ${NEXUS_VAULT_DATA_DIR}"
mkdir -p "${NEXUS_VAULT_DATA_DIR}"

# Generate admin token
print_step "Generating Vaultwarden admin token"
ADMIN_PASSWORD=$(openssl rand -base64 24)
ADMIN_TOKEN=$(docker run --rm -it vaultwarden/server /vaultwarden hash --preset owasp <<< "${ADMIN_PASSWORD}" | tail -n1)

if [ -z "${ADMIN_TOKEN}" ]; then
    print_error "Failed to generate admin token"
    exit 1
fi

# Save plain-text password to a secure file for reference
ADMIN_PASS_FILE="${NEXUS_VAULT_DATA_DIR}/.admin_password"
echo "${ADMIN_PASSWORD}" > "${ADMIN_PASS_FILE}"
chmod 600 "${ADMIN_PASS_FILE}"
print_info "Admin password saved to ${ADMIN_PASS_FILE} (keep this safe!)"

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

# Run Vaultwarden container
print_step "Starting Vaultwarden container"
docker run -d \
    --name vaultwarden \
    --network nexus-net \
    --env DOMAIN="https://${NEXUS_VAULT_SUBDOMAIN}" \
    --env ADMIN_TOKEN="${ADMIN_TOKEN}" \
    --volume "${NEXUS_VAULT_DATA_DIR}:/data/" \
    --restart unless-stopped \
    vaultwarden/server:latest

if [ $? -eq 0 ]; then
    print_success "Vaultwarden container started successfully"
    print_info ""
    print_info "Next steps:"
    print_info "1. Access the admin panel at https://${NEXUS_VAULT_SUBDOMAIN}/admin"
    print_info "2. Use the password stored in ${ADMIN_PASS_FILE} to log in"
    print_info "3. Data will be stored in ${NEXUS_VAULT_DATA_DIR}"
else
    print_error "Failed to start Vaultwarden container"
    exit 1
fi
