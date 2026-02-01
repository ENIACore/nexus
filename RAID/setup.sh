#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

print_header "CONFIGURING RAID ARRAY FOR AUTO-ASSEMBLY"

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

# Check if RAID array exists and is active
if ! grep -q ${NEXUS_REL_RAID_DEVICE} /proc/mdstat; then
    print_error "RAID array ${NEXUS_RAID_DEVICE} is not active"
    print_info "Assemble the array first with: sudo mdadm --assemble --scan"
    exit 1
fi

# Step 1: Configure mdadm.conf with UUID-based configuration
print_step "Configuring /etc/mdadm/mdadm.conf with UUID-based configuration"

# Backup existing config if it exists
if [[ -f /etc/mdadm/mdadm.conf ]]; then
    print_info "Backing up existing mdadm.conf to mdadm.conf.bak"
    cp /etc/mdadm/mdadm.conf /etc/mdadm/mdadm.conf.bak
fi

# Generate new config with active RAID arrays
mdadm --detail --scan > /etc/mdadm/mdadm.conf.new

if [[ -s /etc/mdadm/mdadm.conf.new ]]; then
    mv /etc/mdadm/mdadm.conf.new /etc/mdadm/mdadm.conf
    print_success "mdadm.conf updated successfully"
    print_info "Configuration:"
    cat /etc/mdadm/mdadm.conf
else
    print_error "Failed to generate mdadm.conf"
    if [[ -f /etc/mdadm/mdadm.conf.bak ]]; then
        cp /etc/mdadm/mdadm.conf.bak /etc/mdadm/mdadm.conf
    fi
    exit 1
fi

echo ""

# Step 2: Disable built-in auto-assembly
print_step "Configuring mdadm auto-assembly settings"
if [[ -f /etc/default/mdadm ]]; then
    if grep -q "^AUTOSTART=" /etc/default/mdadm; then
        sed -i 's/^AUTOSTART=.*/AUTOSTART=false/' /etc/default/mdadm
    else
        echo "AUTOSTART=false" >> /etc/default/mdadm
    fi
    print_success "Disabled built-in mdadm auto-assembly"
else
    print_warning "/etc/default/mdadm not found - skipping AUTOSTART configuration"
fi

echo ""

# Step 3: Create systemd service for reliable auto-assembly
print_step "Creating systemd service for RAID auto-assembly"

cat > /etc/systemd/system/mdadm-raid.service << EOF
[Unit]
Description=Assemble RAID array ${NEXUS_RAID_DEVICE}
After=local-fs-pre.target systemd-udev-settle.service
Before=local-fs.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/sbin/mdadm --assemble --scan
ExecStop=/sbin/mdadm --stop ${NEXUS_RAID_DEVICE}

[Install]
WantedBy=multi-user.target
EOF

print_success "Created systemd service at /etc/systemd/system/mdadm-raid.service"

echo ""

# Step 4: Enable and start the systemd service
print_step "Enabling systemd service"
systemctl daemon-reload
systemctl enable mdadm-raid.service

print_success "Systemd service enabled - RAID will auto-assemble on boot"

echo ""

# Step 5: Optionally add to fstab for auto-mount
print_step "Configuring automatic mount in /etc/fstab"

# Check if entry already exists
if grep -q "^${NEXUS_RAID_DEVICE}" /etc/fstab; then
    print_info "Entry already exists in /etc/fstab"
else
    # Detect filesystem type
    FS_TYPE=$(blkid -o value -s TYPE "${NEXUS_RAID_DEVICE}")
    if [[ -z "$FS_TYPE" ]]; then
        FS_TYPE="ext4"
        print_warning "Could not detect filesystem type, assuming ext4"
    fi

    # Add to fstab with nofail option
    echo "${NEXUS_RAID_DEVICE}  ${NEXUS_RAID_MOUNT}  ${FS_TYPE}  defaults,nofail  0  2" >> /etc/fstab
    print_success "Added to /etc/fstab with nofail option"
    print_info "Entry: ${NEXUS_RAID_DEVICE}  ${NEXUS_RAID_MOUNT}  ${FS_TYPE}  defaults,nofail  0  2"
fi

echo ""

# Summary
print_header "SETUP COMPLETE"
print_success "RAID array configured for automatic assembly on boot"
print_info ""
print_info "Configuration summary:"
print_info "• mdadm.conf uses UUID-based identification (prevents drive renaming issues)"
print_info "• systemd service ensures assembly after all drives are detected"
print_info "• fstab entry will auto-mount the array (with nofail for safety)"
print_info ""
print_info "Next steps:"
print_info "1. Reboot to test automatic assembly: sudo reboot"
print_info "2. Check status after boot: ${NEXUS_OPT_DIR}/RAID/status.sh"
print_info "3. Manual control:"
print_info "   - Start: ${NEXUS_OPT_DIR}/RAID/start.sh"
print_info "   - Stop: ${NEXUS_OPT_DIR}/RAID/stop.sh"
print_info "   - Status: ${NEXUS_OPT_DIR}/RAID/status.sh"
