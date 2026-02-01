#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

print_header "STARTING RAID ARRAY"

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

# Assemble RAID array using mdadm.conf (UUID-based)
print_step "Assembling RAID array using UUIDs from /etc/mdadm/mdadm.conf"
if mdadm --assemble --scan; then
    print_success "RAID array assembled"
else
    print_error "Failed to assemble RAID array"
    print_info "Try running: sudo mdadm --assemble --scan --verbose"
    exit 1
fi

# Wait briefly for device to be ready
sleep 1

# Verify RAID is active
print_step "Verifying RAID status"
if ! grep -q ${NEXUS_REL_RAID_DEVICE} /proc/mdstat; then
    print_error "RAID array not found in /proc/mdstat"
    exit 1
fi

# Check RAID health
RAID_STATE=$(mdadm --detail "$NEXUS_RAID_DEVICE" | grep "State :" | awk '{print $3}')
print_info "RAID State: $RAID_STATE"

if [[ "$RAID_STATE" != "clean" ]]; then
    print_warning "RAID state is not clean"
    mdadm --detail "$NEXUS_RAID_DEVICE"
fi

# Create mount point if it doesn't exist
if [[ ! -d "$NEXUS_RAID_MOUNT" ]]; then
    print_step "Creating mount point: $NEXUS_RAID_MOUNT"
    mkdir -p "$NEXUS_RAID_MOUNT"
fi

# Mount the RAID array
print_step "Mounting RAID to $NEXUS_RAID_MOUNT"
if mountpoint -q "$NEXUS_RAID_MOUNT"; then
    print_success "Already mounted"
else
    mount "$NEXUS_RAID_DEVICE" "$NEXUS_RAID_MOUNT"
    print_success "Mounted successfully"
fi

# Display final status
print_step "RAID Status"
mdadm --detail "$NEXUS_RAID_DEVICE" | grep -E "State|Raid Level|Array Size|Active Devices"

print_success "RAID array ready for use at $NEXUS_RAID_MOUNT"
