#!/bin/bash

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)
USER_FUNCS="${BASE_DIR}/scripts/user_funcs.sh"

# Check if nexus user exists
source ${USER_FUNCS}
require_nexus_user

# Create log directory with appropriate permissions
LOG_DIR="/var/log/nexus/cloudflare"

echo "Creating cloudflare log directory at ${LOG_DIR}..."
sudo mkdir -p "${LOG_DIR}"

# Set ownership to nexus user so cron job can write logs
sudo chown nexus:nexus "${LOG_DIR}"
sudo chmod 755 "${LOG_DIR}"

echo "Log directory created successfully"
echo "Logs will be written to: ${LOG_DIR}/dns.log"
