#!/bin/bash
source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"
NEXUS_MC_OPT_DIR="${NEXUS_OPT_DIR}/mc"
NEXUS_MC_PATH="${NEXUS_RAID_MOUNT}/mc-data"
NEXUS_MC_DATA_PATH="${NEXUS_MC_PATH}/data"

# Server settings
MC_TYPE="FABRIC"
MC_VERSION="LATEST"
MC_MEMORY="3G"
MC_DIFFICULTY="normal"
MC_MAX_PLAYERS="10"
MC_VIEW_DISTANCE="10"
MC_OPS="PWRWHL"
MC_WHITELIST="PWRWHL,sulalus"
MC_ENFORCE_WHITELIST="TRUE"

# Mods (auto-downloaded from Modrinth)
MC_MODRINTH_PROJECTS="lithium"

print_header "SETTING UP MINECRAFT SERVER (FABRIC + LITHIUM)"

# Ensure RAID mount exists
require_dir "${NEXUS_RAID_MOUNT}" "RAID mount point"

# Create Minecraft directories
print_step "Creating Minecraft server directories"
mkdir -p "${NEXUS_MC_DATA_PATH}"

# Generate and store RCON password
RCON_PASS_FILE="${NEXUS_MC_PATH}/.rcon_password"
MC_RCON_PASSWORD="$(openssl rand -hex 16)"
echo "${MC_RCON_PASSWORD}" > "${RCON_PASS_FILE}"
chmod 600 "${RCON_PASS_FILE}"
print_info "RCON password stored in ${RCON_PASS_FILE}"

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

# Run itzg/minecraft-server
print_step "Starting Minecraft server container"
docker run -d \
    --name nexus-mc \
    --network nexus-net \
    --restart unless-stopped \
    -e EULA="TRUE" \
    -e TYPE="${MC_TYPE}" \
    -e VERSION="${MC_VERSION}" \
    -e MEMORY="${MC_MEMORY}" \
    -e DIFFICULTY="${MC_DIFFICULTY}" \
    -e MAX_PLAYERS="${MC_MAX_PLAYERS}" \
    -e VIEW_DISTANCE="${MC_VIEW_DISTANCE}" \
    -e OPS="${MC_OPS}" \
    -e WHITELIST="${MC_WHITELIST}" \
    -e ENFORCE_WHITELIST="${MC_ENFORCE_WHITELIST}" \
    -e TZ="America/Chicago" \
    -e ENABLE_RCON="true" \
    -e RCON_PASSWORD="${MC_RCON_PASSWORD}" \
    -e SERVER_PORT="25565" \
    -e MODRINTH_PROJECTS="${MC_MODRINTH_PROJECTS}" \
    -v "${NEXUS_MC_DATA_PATH}":/data \
    itzg/minecraft-server:latest
#    -p 25565:25565 \ Now managed by nginx stream

if [ $? -eq 0 ]; then
    print_success "Minecraft server container started successfully"
    print_info ""
    print_info "Next steps:"
    print_info "1. Connect via Minecraft client at <server-ip>:25565"
    print_info "2. Monitor startup progress: docker logs -f nexus-mc"
    print_info "3. World data stored in ${NEXUS_MC_DATA_PATH}"
    print_info "4. RCON password stored in ${RCON_PASS_FILE}"
else
    print_error "Failed to start Minecraft server container"
    exit 1
fi
