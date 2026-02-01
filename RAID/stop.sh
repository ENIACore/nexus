#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

print_header "STOPPING RAID ARRAY"

# Must be root
if [[ $EUID -ne 0 ]]; then
    print_error "This script must be run as root"
    exit 1
fi

# Ensure RAID device is configured
if [[ -z "${NEXUS_RAID_DEVICE}" ]]; then
    print_error "RAID device not configured in /etc/nexus/conf/conf.sh"
    exit 1
fi

# Unmount if mounted
print_step "Checking mount status"
if mountpoint -q "$NEXUS_RAID_MOUNT"; then
    print_step "Unmounting $NEXUS_RAID_MOUNT"

    # Sync filesystem before unmounting
    sync

    umount "$NEXUS_RAID_MOUNT"
    print_success "Unmounted"
else
    print_success "Not mounted"
fi

# Stop RAID array if active
print_step "Checking RAID array status"
if grep -q ${NEXUS_REL_RAID_DEVICE} /proc/mdstat; then
    print_step "Stopping RAID array"
    mdadm --stop "$NEXUS_RAID_DEVICE"
    print_success "Stopped"
else
    print_success "RAID array not active"
fi

print_success "RAID safely stopped - Safe to disconnect drives"
