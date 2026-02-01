#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"

print_header "RAID ARRAY STATUS"

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

# Check if RAID array exists
if ! grep -q ${NEXUS_REL_RAID_DEVICE} /proc/mdstat; then
    print_warning "RAID array ${NEXUS_RAID_DEVICE} is not active"
    print_info "Run ${NEXUS_OPT_DIR}/RAID/start.sh to start the array"
    exit 0
fi

# Show /proc/mdstat
print_step "RAID Array Overview (/proc/mdstat)"
cat /proc/mdstat | grep -A 3 ${NEXUS_REL_RAID_DEVICE}
echo ""

# Show detailed mdadm status
print_step "Detailed RAID Status"
mdadm --detail "$NEXUS_RAID_DEVICE"
echo ""

# Show mount status
print_step "Mount Status"
if mountpoint -q "$NEXUS_RAID_MOUNT"; then
    print_success "Mounted at $NEXUS_RAID_MOUNT"
    df -h "$NEXUS_RAID_MOUNT" | tail -n 1
else
    print_warning "Not mounted"
    print_info "Run ${NEXUS_OPT_DIR}/RAID/start.sh to mount the array"
fi
echo ""

# Show UUID
print_step "Array UUID"
UUID=$(mdadm --detail "$NEXUS_RAID_DEVICE" | grep UUID | awk '{print $NF}')
print_info "UUID: ${UUID}"
echo ""

# Check mdadm.conf
print_step "mdadm.conf Configuration"
if [[ -f /etc/mdadm/mdadm.conf ]]; then
    grep "^ARRAY" /etc/mdadm/mdadm.conf || print_warning "No ARRAY entries found in mdadm.conf"
else
    print_error "mdadm.conf not found at /etc/mdadm/mdadm.conf"
fi
