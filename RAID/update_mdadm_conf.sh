#!/bin/bash
# RAID Reassembly Script (UUID-based)

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)
RAID_CONFIG="${BASE_DIR}/keys/RAID.sh"

# Ensure config exists
if [[ ! -f "$RAID_CONFIG" ]]; then
    echo -e "${RED}RAID config not found: $RAID_CONFIG${NC}"
    exit 1
fi

source "$RAID_CONFIG"

# Must be root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}This script must be run as root${NC}"
    exit 1
fi

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}       Update mdadm.conf                ${NC}"
echo -e "${YELLOW}========================================${NC}"
echo

echo -e "${YELLOW}Updating mdadm.conf${NC}"

# Backup the old config
cp /etc/mdadm/mdadm.conf /etc/mdadm/mdadm.conf.bak
echo -e "${GREEN}Backed up to mdadm.conf.bak${NC}"

# Generate new config with all active RAID arrays
mdadm --detail --scan > /etc/mdadm/mdadm.conf.new

if [[ -s /etc/mdadm/mdadm.conf.new ]]; then
    mv /etc/mdadm/mdadm.conf.new /etc/mdadm/mdadm.conf
    echo -e "${GREEN}mdadm.conf updated successfully${NC}"
else
    echo -e "${RED}Error: mdadm --detail --scan produced no output${NC}"
    # Restore from backup if generation failed
    cp /etc/mdadm/mdadm.conf.bak /etc/mdadm/mdadm.conf
    exit 1
fi

# Stop array if running
if grep -q "^$(basename "$RAID_DEVICE") " /proc/mdstat; then
    echo -e "${YELLOW}Unmounting mount point${NC}"
    umount $MOUNT_POINT
    echo -e "${YELLOW}Stopping array $RAID_DEVICE...${NC}"
    mdadm --stop "$RAID_DEVICE"
else
    echo -e "${GREEN}Array $RAID_DEVICE not active, skipping stop.${NC}"
fi

# Reassemble array
echo -e "${YELLOW}Reassembling array using UUIDs...${NC}"
mdadm --assemble --scan

# Verify
echo -e "${YELLOW}Verifying array status...${NC}"
cat /proc/mdstat
mdadm --detail "$RAID_DEVICE"

echo -e "${YELLOW}Remounting filesystem...${NC}"
mount $MOUNT_POINT
echo -e "${GREEN}RAID rebuild complete${NC}"
