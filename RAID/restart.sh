#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

print_header "RESTARTING DEGRADED RAID ARRAY"

if [[ $EUID -ne 0 ]]; then
    print_error "This script must be run as root"
    exit 1
fi

print_step "Stopping services running at mount point (dependent on specific server setup - default is mc, qbit, and jellyfin)"
docker stop jellyfin
docker stop nexus-mc
docker stop qbittorrent

# Stop the array
print_step "Stopping RAID array"
"${NEXUS_OPT_DIR}/RAID/stop.sh"

# Reassemble using UUID from mdadm.conf
print_step "Reassembling RAID array from UUID configuration"
mdadm --assemble --scan

if grep -q ${NEXUS_REL_RAID_DEVICE} /proc/mdstat; then
    print_success "RAID array reassembled"
else
    print_error "Failed to reassemble RAID array"
    exit 1
fi

# Mount
print_step "Mounting RAID array"
mount "$NEXUS_RAID_DEVICE" "$NEXUS_RAID_MOUNT"

if mountpoint -q "$NEXUS_RAID_MOUNT"; then
    print_success "Mounted at $NEXUS_RAID_MOUNT"
else
    print_error "Failed to mount"
    exit 1
fi

# Show status
"${NEXUS_OPT_DIR}/RAID/status.sh"


print_step "Starting services running at mount point (dependent on specific server setup - default is mc, qbit, and jellyfin)"
docker start jellyfin
docker start nexus-mc
docker start qbittorrent
