#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

print_header "UPDATING DNS"

# Get cloudflare api key for nexus
NEXUS_CF_API_KEY_FILE="${NEXUS_ETC_DIR}/keys/cloudflare.sh"
require_file ${NEXUS_CF_API_KEY_FILE} "Cloudflare api key file containing NEXUS_CF_API_KEY variable"
source ${NEXUS_CF_API_KEY_FILE}

# Initialize logger
NEXUS_CF_LOG_DIR="${NEXUS_LOG_DIR}/cloudflare"
NEXUS_CF_LOG_FILE="${NEXUS_CF_LOG_DIR}/dns.log"
NEXUS_CF_LOG_MAX_LINES=100
init_logger "${NEXUS_CF_LOG_FILE}" "${NEXUS_CF_LOG_MAX_LINES}"

# Set ownership to nexus user so cron job can write logs - It will be set to root now
sudo chown -R ${NEXUS_USER}:${NEXUS_USER} "${NEXUS_CF_LOG_DIR}"
sudo chmod 755 "${NEXUS_CF_LOG_DIR}"

# Get public IPV4 address
log "Detecting public IPv4 address..."
PUBLIC_IPV4=$(curl -s4 https://api.ipify.org || curl -s4 https://icanhazip.com || curl -s4 https://ifconfig.me)
if [[ -z "$PUBLIC_IPV4" ]]; then
    log "ERROR: Could not determine public IP address"
    exit 1
fi
log "Current IPv4 address: ${PUBLIC_IPV4}"

# Get Zone ID for domain
log "Retrieving Zone ID for ${NEXUS_DOMAIN}..."
ZONE_ID=$(curl -s "https://api.cloudflare.com/client/v4/zones?name=${NEXUS_DOMAIN}" -H "Authorization: Bearer ${NEXUS_CF_API_KEY}" | jq -r '.result[0].id')
if [[ -z "$ZONE_ID" || "$ZONE_ID" == "null" ]]; then
    log "ERROR: Could not get Zone ID for ${NEXUS_DOMAIN}"
    exit 1
fi
log "Zone ID: ${ZONE_ID}"

# Get A record IDs for domain
log "Retrieving DNS record IDs..."
ROOT_RECORD_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records?name=${NEXUS_DOMAIN}&type=A" -H "Authorization: Bearer ${NEXUS_CF_API_KEY}" | jq -r '.result[0].id')
WILDCARD_RECORD_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records?name=${NEXUS_WILDCARD_DOMAIN}&type=A" -H "Authorization: Bearer ${NEXUS_CF_API_KEY}" | jq -r '.result[0].id')

if [[ -z "$ROOT_RECORD_ID" || "$ROOT_RECORD_ID" == "null" ]]; then
    log "ERROR: Could not get Record ID for ${NEXUS_DOMAIN}"
    exit 1
fi
if [[ -z "$WILDCARD_RECORD_ID" || "$WILDCARD_RECORD_ID" == "null" ]]; then
    log "ERROR: Could not get Record ID for ${NEXUS_WILDCARD_DOMAIN}"
    exit 1
fi
log "Root Record ID: ${ROOT_RECORD_ID}"
log "Wildcard Record ID: ${WILDCARD_RECORD_ID}"

# Update root A record to new IP address
log "Updating A record for ${NEXUS_DOMAIN} -> ${PUBLIC_IPV4}"
ROOT_RECORD_RESPONSE=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records/${ROOT_RECORD_ID}" -H "Authorization: Bearer ${NEXUS_CF_API_KEY}" -H "Content-Type: application/json" --data "{\"type\":\"A\",\"name\":\"${NEXUS_DOMAIN}\",\"content\":\"${PUBLIC_IPV4}\",\"ttl\":1,\"proxied\":true}")

# Check if update was successful
SUCCESS=$(echo "${ROOT_RECORD_RESPONSE}" | jq -r '.success')
if [[ "${SUCCESS}" == "true" ]]; then
    log "SUCCESS: Updated ${NEXUS_DOMAIN} to ${PUBLIC_IPV4}"
else
    log "ERROR: Failed to update ${NEXUS_DOMAIN}"
    log "Response: ${ROOT_RECORD_RESPONSE}"
    exit 1
fi

# Update wildcard A record to new IP address
log "Updating A record for ${NEXUS_WILDCARD_DOMAIN} -> ${PUBLIC_IPV4}"
WILDCARD_RECORD_RESPONSE=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records/${WILDCARD_RECORD_ID}" -H "Authorization: Bearer ${NEXUS_CF_API_KEY}" -H "Content-Type: application/json" --data "{\"type\":\"A\",\"name\":\"${NEXUS_WILDCARD_DOMAIN}\",\"content\":\"${PUBLIC_IPV4}\",\"ttl\":1,\"proxied\":true}")

# Check if update was successful
SUCCESS=$(echo "${WILDCARD_RECORD_RESPONSE}" | jq -r '.success')
if [[ "${SUCCESS}" == "true" ]]; then
    log "SUCCESS: Updated ${NEXUS_WILDCARD_DOMAIN} to ${PUBLIC_IPV4}"
else
    log "ERROR: Failed to update ${NEXUS_WILDCARD_DOMAIN}"
    log "Response: ${WILDCARD_RECORD_RESPONSE}"
    exit 1
fi

log "DNS Update Complete"
