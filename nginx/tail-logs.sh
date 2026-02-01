#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"

CONTAINER_NAME="nexus-proxy"
NEXUS_NGINX_LOG_DIR="${NEXUS_LOG_DIR}/nginx"
NEXUS_NGINX_ACCESS_LOG="${NEXUS_NGINX_LOG_DIR}/access.log"
NEXUS_NGINX_ERROR_LOG="${NEXUS_NGINX_LOG_DIR}/error.log"

# Check if container exists
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    print_error "Container '${CONTAINER_NAME}' not found"
    exit 1
fi

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    print_warning "Container '${CONTAINER_NAME}' is not running"
    print_info "Showing logs from stopped container..."
fi

# Check if log files exist
if [ ! -f "${NEXUS_NGINX_ACCESS_LOG}" ] && [ ! -f "${NEXUS_NGINX_ERROR_LOG}" ]; then
    print_error "No log files found in ${NEXUS_NGINX_LOG_DIR}"
    exit 1
fi

print_header "TAILING NGINX LOGS"
print_info "Log directory: ${NEXUS_NGINX_LOG_DIR}"
print_info "Press Ctrl+C to stop"
echo ""

# Tail both access and error logs, with labels
tail -f -n 100 "${NEXUS_NGINX_ACCESS_LOG}" "${NEXUS_NGINX_ERROR_LOG}" 2>/dev/null | \
    awk '/==> \/var\/log\/nexus\/nginx\/access.log <==/{print "\n\033[0;32m[ACCESS]\033[0m"; next} 
         /==> \/var\/log\/nexus\/nginx\/error.log <==/{print "\n\033[0;31m[ERROR]\033[0m"; next} 
         {print}'
