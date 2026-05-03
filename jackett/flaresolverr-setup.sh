#!/bin/bash
# FlareSolverr is used as a proxy server to bypass Cloudflare protection
source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_FLARESOLVERR_OPT_DIR="${NEXUS_OPT_DIR}/flaresolverr"

print_header "SETTING UP FLARESOLVERR"

# Ensure media services path exists
require_dir "${NEXUS_MEDIA_SERVICES_PATH}" "Media services path"

# Ensure docker network exists
if ! docker network inspect nexus-net >/dev/null 2>&1; then
    print_step "Creating Docker network 'nexus-net'"
    if ! docker network create \
        --driver bridge \
        --subnet 172.18.0.0/16 \
        --gateway 172.18.0.1 \
        nexus-net >/dev/null 2>&1; then
        print_error "Failed to create Docker network 'nexus-net' (subnet or gateway already in use, choose a new range)"
        exit 1
    fi
fi

# Run FlareSolverr container
print_step "Starting FlareSolverr container"
docker run -d \
    --name flaresolverr \
    --network nexus-net \
    -e LOG_LEVEL=info \
    -e TZ=Etc/UTC \
    --restart=unless-stopped \
    ghcr.io/flaresolverr/flaresolverr:latest
# -p 8191:8191 \

if [ $? -eq 0 ]; then
    print_success "FlareSolverr container started successfully"
    print_info ""
    print_info "Next steps:"
    print_info "1. FlareSolverr is accessible to other containers on nexus-net at http://flaresolverr:8191"
    print_info "2. In Jackett, set the FlareSolverr API URL to http://flaresolverr:8191"
    print_info "3. Test connectivity with: curl http://flaresolverr:8191/v1"
else
    print_error "Failed to start FlareSolverr container"
    exit 1
fi
