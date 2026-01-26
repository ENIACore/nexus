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
echo -e "${YELLOW}      Stop RAID Array                   ${NC}"
echo -e "${YELLOW}========================================${NC}"
echo

# Unmount if mounted
if mountpoint -q "$MOUNT_POINT"; then
    echo -e "${YELLOW}Unmounting $MOUNT_POINT...${NC}"
    
    # Sync filesystem before unmounting
    sync
    
    umount "$MOUNT_POINT"
    echo -e "${GREEN}✓ Unmounted${NC}"
else
    echo -e "${GREEN}✓ Not mounted${NC}"
fi

echo

# Stop RAID array if active
if grep -q ${REL_RAID_DEVICE} /proc/mdstat; then
    echo -e "${YELLOW}Stopping RAID array...${NC}"
    mdadm --stop "$RAID_DEVICE"
    echo -e "${GREEN}✓ Stopped${NC}"
else
    echo -e "${GREEN}✓ RAID array not active${NC}"
fi

echo

echo -e "${GREEN}✓ RAID safely stopped. Safe to disconnect.${NC}"
