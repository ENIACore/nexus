#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_NGINX_ETC_DIR="/etc/nexus/nginx"
NEXUS_NGINX_OPT_DIR="/opt/nexus/nginx"

print_header "UPDATING NEXUS REVERSE PROXY CONFIGURATION"

# Remove old configuration files
print_step "Removing old configuration files"
rm -rf "${NEXUS_NGINX_ETC_DIR}/conf"
rm -rf "${NEXUS_NGINX_ETC_DIR}/conf.d"
rm -rf "${NEXUS_NGINX_ETC_DIR}/snippets"

# Copy fresh configuration from opt
print_step "Copying updated nginx configuration to /etc/nexus/nginx"
cp -r "${NEXUS_NGINX_OPT_DIR}/conf" "${NEXUS_NGINX_ETC_DIR}/"
cp -r "${NEXUS_NGINX_OPT_DIR}/conf.d" "${NEXUS_NGINX_ETC_DIR}/"
cp -r "${NEXUS_NGINX_OPT_DIR}/snippets" "${NEXUS_NGINX_ETC_DIR}/"

print_success "Configuration files updated successfully"
print_info "Run ${NEXUS_NGINX_OPT_DIR}/reload.sh to apply changes to the running container"
