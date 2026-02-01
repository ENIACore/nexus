#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_NGINX_ETC_DIR="/etc/nexus/nginx"
NEXUS_NGINX_OPT_DIR="/opt/nexus/nginx"

print_header "CREATING NEXUS REVERSE PROXY"

# Ensure letsencrypt files present 
require_dir "/etc/letsencrypt/live/${NEXUS_DOMAIN}" "Letsencrypt directory containing SSL certificates" 

# Ensure docker network exists
if ! docker network inspect nexus >/dev/null 2>&1; then
    print_step "Creating Docker network 'nexus'"
    docker network create --driver bridge --subnet 172.18.0.0/16 nexus-net >/dev/null
fi

# Copy nginx configuration from opt to /etc/nexus/nginx
print_step "Copying nginx configuration to /etc/nexus/nginx"
mkdir -p "${NEXUS_NGINX_ETC_DIR}"
cp -r "${NEXUS_NGINX_OPT_DIR}/conf" "${NEXUS_NGINX_ETC_DIR}/"
cp -r "${NEXUS_NGINX_OPT_DIR}/conf.d" "${NEXUS_NGINX_ETC_DIR}/"
cp -r "${NEXUS_NGINX_OPT_DIR}/snippets" "${NEXUS_NGINX_ETC_DIR}/"

# Create sites-enabled directory
print_step "Creating sites-enabled directory at ${NEXUS_NGINX_ETC_DIR}/sites-enabled"
mkdir -p "${NEXUS_NGINX_ETC_DIR}/sites-enabled"

NEXUS_NGINX_LOG_DIR="${NEXUS_LOG_DIR}/nginx"
print_step "Creating container log dir at ${NEXUS_NGINX_LOG_DIR}"
mkdir -p "${NEXUS_NGINX_LOG_DIR}"


print_info "To enable sites:"
print_info "1. Move site configs to ${NEXUS_NGINX_ETC_DIR}/sites-enabled directory"
print_info "2. Run ${NEXUS_NGINX_OPT_DIR}/update.sh script to ensure most up to date snippets and conf files"
print_info "3. Run ${NEXUS_NGINX_OPT_DIR}/reload.sh script to reload running nexus proxy container"

# Create nginx log directory
print_step "Creating nginx log directory"
mkdir -p /var/log/nexus/nginx

# Then in your docker run command, replace the --log-driver lines with:
docker run -d \
    --name nexus-proxy \
    --restart unless-stopped \
    --network nexus-net \
    --ip 172.18.0.254 \
    -p 80:80 \
    -p 443:443 \
    --read-only \
    -v "${NEXUS_NGINX_ETC_DIR}/conf/nginx.conf:/etc/nginx/nginx.conf:ro" \
    -v "${NEXUS_NGINX_ETC_DIR}/conf.d:/etc/nginx/conf.d:ro" \
    -v "${NEXUS_NGINX_ETC_DIR}/snippets:/etc/nginx/snippets:ro" \
    -v "${NEXUS_NGINX_ETC_DIR}/sites-enabled:/etc/nginx/sites-enabled:ro" \
    -v "/etc/letsencrypt:/etc/letsencrypt:ro" \
    -v "${NEXUS_NGINX_LOG_DIR}:/var/log/nginx:rw" \
    --tmpfs /var/cache/nginx:rw,noexec,nosuid,size=100m \
    --tmpfs /var/run:rw,noexec,nosuid,size=10m \
    --health-cmd="nginx -t" \
    --health-interval=30s \
    --health-timeout=3s \
    --health-retries=3 \
    --health-start-period=30s \
    nginx:latest

if [ $? -eq 0 ]; then
    print_success "Nexus reverse proxy container started successfully"
else
    print_error "Failed to start nexus reverse proxy container"
    exit 1
fi
