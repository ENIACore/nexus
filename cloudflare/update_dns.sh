#!/bin/bash

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)
LOG_FUNCS="${BASE_DIR}/scripts/log_funcs.sh"
CF_API_KEY="${BASE_DIR}/keys/cloudflare.sh"

LOG_FILE="/var/log/nexus/cloudflare/dns.log"
MAX_LOG_LINES=100

DOMAIN="lamkin.dev"
ROOT_RECORD="lamkin.dev"
WILDCARD_RECORD="*.lamkin.dev"


source ${LOG_FUNCS}
source ${CF_API_KEY}

# Get public IPV4 address
log "Detecting public IPv4 address..."
PUBLIC_IPV4=$(curl -s4 https://api.ipify.org || curl -s4 https://icanhazip.com || curl -s4 https://ifconfig.me)
if [[ -z "$PUBLIC_IPV4" ]]; then
    log "ERROR: Could not determine public IP address"
    exit 1
fi
log "Current IPv4 address: ${PUBLIC_IPV4}"

# Get Zone ID for domain
log "Retrieving Zone ID for ${DOMAIN}..."
ZONE_ID=$(curl -s https://api.cloudflare.com/client/v4/zones?name=${DOMAIN} -H "Authorization: Bearer ${CF_API_KEY}" | jq -r '.result[0].id')
if [[ -z "$ZONE_ID" || "$ZONE_ID" == "null" ]]; then
    log "ERROR: Could not get Zone ID for ${DOMAIN}"
    exit 1
fi
log "Zone ID: ${ZONE_ID}"

# Get A record IDs for domain
log "Retrieving DNS record IDs..."
ROOT_RECORD_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records?name=${ROOT_RECORD}&type=A" -H "Authorization: Bearer ${CF_API_KEY}" | jq -r '.result[0].id')
WILDCARD_RECORD_ID=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records?name=${WILDCARD_RECORD}&type=A" -H "Authorization: Bearer ${CF_API_KEY}" | jq -r '.result[0].id')

if [[ -z "$ROOT_RECORD_ID" || "$ROOT_RECORD_ID" == "null" ]]; then
    log "ERROR: Could not get Record ID for ${ROOT_RECORD}"
    exit 1
fi

if [[ -z "$WILDCARD_RECORD_ID" || "$WILDCARD_RECORD_ID" == "null" ]]; then
    log "ERROR: Could not get Record ID for ${WILDCARD_RECORD}"
    exit 1
fi

log "Root Record ID: ${ROOT_RECORD_ID}"
log "Wildcard Record ID: ${WILDCARD_RECORD_ID}"

# Update root A record to new IP address
log "Updating A record for ${ROOT_RECORD} -> ${PUBLIC_IPV4}"
ROOT_RECORD_RESPONSE=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records/${ROOT_RECORD_ID}" -H "Authorization: Bearer ${CF_API_KEY}" -H "Content-Type: application/json" --data "{\"type\":\"A\",\"name\":\"${ROOT_RECORD}\",\"content\":\"${PUBLIC_IPV4}\",\"ttl\":1,\"proxied\":true}")

# Check if update was successful
SUCCESS=$(echo "${ROOT_RECORD_RESPONSE}" | jq -r '.success')
if [[ "${SUCCESS}" == "true" ]]; then
    log "SUCCESS: Updated ${ROOT_RECORD} to ${PUBLIC_IPV4}"
else
    log "ERROR: Failed to update ${ROOT_RECORD}"
    log "Response: ${ROOT_RECORD_RESPONSE}"
    exit 1
fi

# Update wildcard A record to new IP address
log "Updating A record for ${WILDCARD_RECORD} -> ${PUBLIC_IPV4}"
WILDCARD_RECORD_RESPONSE=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records/${WILDCARD_RECORD_ID}" -H "Authorization: Bearer ${CF_API_KEY}" -H "Content-Type: application/json" --data "{\"type\":\"A\",\"name\":\"${WILDCARD_RECORD}\",\"content\":\"${PUBLIC_IPV4}\",\"ttl\":1,\"proxied\":true}")

# Check if update was successful
SUCCESS=$(echo "${WILDCARD_RECORD_RESPONSE}" | jq -r '.success')
if [[ "${SUCCESS}" == "true" ]]; then
    log "SUCCESS: Updated ${WILDCARD_RECORD} to ${PUBLIC_IPV4}"
else
    log "ERROR: Failed to update ${WILDCARD_RECORD}"
    log "Response: ${WILDCARD_RECORD_RESPONSE}"
    exit 1
fi

log "DNS Update Complete"
