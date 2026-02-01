#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

print_header "CONFIGURING CLOUDFLARE COUNTRY BLOCKING"

# Get cloudflare api key for nexus
NEXUS_CF_API_KEY_FILE="${NEXUS_ETC_DIR}/keys/cloudflare.sh"
require_file ${NEXUS_CF_API_KEY_FILE} "Cloudflare api key file containing NEXUS_CF_API_KEY variable"
source ${NEXUS_CF_API_KEY_FILE}

# Initialize logger
NEXUS_CF_LOG_DIR="${NEXUS_LOG_DIR}/cloudflare"
NEXUS_CF_LOG_FILE="${NEXUS_CF_LOG_DIR}/firewall.log"
NEXUS_CF_LOG_MAX_LINES=100
init_logger "${NEXUS_CF_LOG_FILE}" "${NEXUS_CF_LOG_MAX_LINES}"

# Set ownership to nexus user so cron job can write logs - It will be set to root now
sudo chown -R ${NEXUS_USER}:${NEXUS_USER} "${NEXUS_CF_LOG_DIR}"
sudo chmod 755 "${NEXUS_CF_LOG_DIR}"

# Get Zone ID for domain
log "Retrieving Zone ID for ${NEXUS_DOMAIN}..."
ZONE_ID=$(curl -s "https://api.cloudflare.com/client/v4/zones?name=${NEXUS_DOMAIN}" -H "Authorization: Bearer ${NEXUS_CF_API_KEY}" | jq -r '.result[0].id')
if [[ -z "$ZONE_ID" || "$ZONE_ID" == "null" ]]; then
    log "ERROR: Could not get Zone ID for ${NEXUS_DOMAIN}"
    exit 1
fi
log "Zone ID: ${ZONE_ID}"

# Configure firewall rule to block countries outside the US
log "Configuring firewall rule to block non-US traffic..."
FIREWALL_RESPONSE=$(curl -s -X PUT \
    "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/rulesets/phases/http_request_firewall_custom/entrypoint" \
    -H "Authorization: Bearer ${NEXUS_CF_API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{
        "rules": [
            {
                "description": "Block countries outside the US",
                "expression": "(ip.src.country ne \"US\")",
                "action": "block"
            }
        ]
    }')

# Check if update was successful
SUCCESS=$(echo "${FIREWALL_RESPONSE}" | jq -r '.success')
if [[ "${SUCCESS}" == "true" ]]; then
    log "SUCCESS: Configured firewall to block non-US traffic"
else
    log "ERROR: Failed to configure firewall rule"
    log "Response: ${FIREWALL_RESPONSE}"
    exit 1
fi

log "Country blocking configuration complete"
