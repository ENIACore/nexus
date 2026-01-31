#!/bin/bash

source "/etc/nexus/conf/conf.sh"

# Ensure nexus user exists
ensure_nexus_user

# Create log directory with appropriate permissions
NEXUS_CF_LOG_DIR="${NEXUS_LOG_DIR}/cloudflare"

echo "Creating nexus cloudflare log directory at ${NEXUS_CF_LOG_DIR}..."
sudo mkdir -p "${NEXUS_CF_LOG_DIR}"

# Set ownership to nexus user so cron job can write logs
sudo chown ${NEXUS_USER}:${NEXUS_USER} "${NEXUS_CF_LOG_DIR}"
sudo chmod 755 "${NEXUS_CF_LOG_DIR}"

echo "Log directory created successfully"
echo "Logs will be written to: ${NEXUS_CF_LOG_DIR}/cf-dns.log"
