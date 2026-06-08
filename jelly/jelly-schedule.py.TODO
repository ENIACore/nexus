#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

print_header "SCHEDULING SUBTITLE DOWNLOADER - BEOFRE USE MAKE SURE MEDIA LIBRARY HAS BEEN PROCESSED BY ENIACore's Media Library Manager!"

# Ensure variables are present
require_file "${NEXUS_ETC_DIR}/keys/mlm.sh" "mlm api key file containing standard mlm configurations"
source "${NEXUS_ETC_DIR}/keys/mlm.sh"

print_step "Ensuring Media Library Manager tool is in path"
curl -fsSL https://raw.githubusercontent.com/ENIACore/media-library-manager/main/install.py -o /tmp/mlm-install.py && sudo python3 /tmp/mlm-install.py; rm -f /tmp/mlm-install.py

NEXUS_MLM_CRON_SCHEDULE="0 */2 * * *"
NEXUS_MLM_CRON_FILE="/etc/cron.d/nexus-mlm-subtitle"

# Ensure nexus user exists
ensure_nexus_user

# Check if cron job already exists
if [[ -f "${NEXUS_MLM_CRON_FILE}" ]]; then
    echo "System cron job already exists at ${NEXUS_MLM_CRON_FILE}"
    exit 1
fi

print_step "Creating system cron job at ${NEXUS_MLM_CRON_FILE}..."

mkdir -p "${NEXUS_MLM_MANAGER_PATH}/logs"

sudo tee "${NEXUS_MLM_CRON_FILE}" > /dev/null << EOF
# Subtitle updater - runs as root
# Downloads subtitles every 2 hours
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
# Run every 2 hours
${NEXUS_MLM_CRON_SCHEDULE} root mlm -mode=subtitle -dry-run=false -movie-path="${NEXUS_MLM_MOVIE_PATH}" -show-path="${NEXUS_MLM_SHOW_PATH}" -manager-path="${NEXUS_MLM_MANAGER_PATH}" -log-stdout=false -torrent-path="${NEXUS_MLM_TORRENT_PATH}" -incomplete-path="${NEXUS_MLM_INCOMPLETE_PATH}" -interactive=false -tmdb-api-key="${NEXUS_MLM_TMDB_API_KEY}" -limit=80 -os-api-key="${NEXUS_MLM_OS_API_KEY}" -os-user-agent="${NEXUS_MLM_OS_USER_AGENT}" -os-user="${NEXUS_MLM_OS_USER}" -os-pass="${NEXUS_MLM_OS_PASS}" >> "${NEXUS_MLM_MANAGER_PATH}/logs/cronjob.log" 2>&1
EOF

# Set proper permissions for system cron file
sudo chmod 644 "${NEXUS_MLM_CRON_FILE}"

print_info "System cron job created successfully"
print_info "Nexus subtitle updater will run every 2 hours (processing 80 records) as user '${NEXUS_USER}'"
