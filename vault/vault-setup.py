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

# Ensure argon2 is installed
if ! command -v argon2 >/dev/null 2>&1; then
    print_step "Installing argon2"
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update -qq && apt-get install -y argon2
    elif command -v dnf >/dev/null 2>&1; then
        dnf install -y argon2
    elif command -v yum >/dev/null 2>&1; then
        yum install -y argon2
    elif command -v pacman >/dev/null 2>&1; then
        pacman -S --noconfirm argon2
    else
        print_error "No supported package manager found to install argon2"
        exit 1
    fi

    if ! command -v argon2 >/dev/null 2>&1; then
        print_error "argon2 installation failed"
        exit 1
    fi
fi

# Generate admin password (this is what you'll type at the login prompt)
print_step "Generating Vaultwarden admin password"
ADMIN_PASSWORD=$(openssl rand -base64 48)

# Generate argon2id PHC hash of the password (Bitwarden defaults: m=64MiB, t=3, p=4)
print_step "Hashing admin password with argon2id"
ADMIN_TOKEN=$(echo -n "${ADMIN_PASSWORD}" | argon2 "$(openssl rand -base64 32)" -e -id -k 65540 -t 3 -p 4)

if [ -z "${ADMIN_TOKEN}" ]; then
    print_error "Failed to generate argon2id PHC string"
    exit 1
fi

# Save the plaintext password (NOT the hash) since that's what you log in with
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
# Note: ADMIN_TOKEN here is the argon2id PHC hash, not the plaintext password.
# Passing via -e avoids the docker-compose $$ escaping issue entirely.
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
