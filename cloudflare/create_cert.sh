#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

print_header "CREATING DNS CERTIFICATE"

# !Prior to running script
# Add cloudflare.ini file to /etc/nexus/keys/ with API Key `dns_cloudflare_api_token = <token>`
# Chmod 600 cloudflare.ini

NEXUS_CF_API_KEY_FILE="${NEXUS_ETC_DIR}/keys/cloudflare.ini"
DRY_RUN=""

# Ensure ini file is present 
require_file "${NEXUS_CF_INI_FILE}" "Cloudflare ini file containing cloudflare api key" 

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run|-d)
            DRY_RUN="--dry-run"
            print_info "Running in dry-run mode (no certificates will be created)"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Usage: $0 [--dry-run|-d]"
            exit 1
            ;;
    esac
done

# Verify credentials file exists
if [[ ! -f "${NEXUS_CF_INI_FILE}" ]]; then
    print_error "Cloudflare credentials file not found at ${NEXUS_CF_INI_FILE}"
    exit 1
fi

if [[ -n "${DRY_RUN}" ]]; then
    print_step "Testing SSL certificate creation for ${NEXUS_DOMAIN} and ${NEXUS_WILDCARD_DOMAIN}..."
else
    print_step "Creating SSL certificate for ${NEXUS_DOMAIN} and ${NEXUS_WILDCARD_DOMAIN}..."
fi

sudo certbot certonly \
  --dns-cloudflare \
  --dns-cloudflare-credentials "${NEXUS_CF_INI_FILE}" \
  --dns-cloudflare-propagation-seconds 60 \
  -d "${NEXUS_WILDCARD_DOMAIN}" \
  -d "${NEXUS_DOMAIN}" \
  ${DRY_RUN}

if [[ $? -ne 0 ]]; then
    print_error "Certificate creation failed"
    exit 1
fi

print_success "Certificate created successfully"

sleep 1

print_step "Verifying certbot renewal timer is working..."
sudo systemctl status certbot.timer

print_step "Verifying certbot renewal functions..."
sudo certbot renew --dry-run

if [[ $? -eq 0 ]]; then
    print_success "Certificate renewal test passed"
else
    print_error "Certificate renewal test failed"
    exit 1
fi

print_success "Certificate setup complete"
