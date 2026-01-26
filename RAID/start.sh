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
echo -e "${YELLOW}      Start RAID Array                  ${NC}"
echo -e "${YELLOW}========================================${NC}"
echo

# Assemble RAID array using mdadm.conf (UUID-based)
echo -e "${YELLOW}Assembling RAID array using UUIDs from mdadm.conf...${NC}"
if mdadm --assemble --scan; then
    echo -e "${GREEN}✓ RAID array assembled${NC}"
else
    echo -e "${RED}Error: Failed to assemble RAID array${NC}"
    exit 1
fi

echo

# Wait briefly for device to be ready
sleep 1

# Verify RAID is active
echo -e "${YELLOW}Verifying RAID status...${NC}"
if ! grep -q ${REL_RAID_DEVICE} /proc/mdstat; then
    echo -e "${RED}Error: RAID array not found in /proc/mdstat${NC}"
    exit 1
fi

# Check RAID health
RAID_STATE=$(mdadm --detail "$RAID_DEVICE" | grep "State :" | awk '{print $3}')
echo "RAID State: $RAID_STATE"

if [[ "$RAID_STATE" != "clean" ]]; then
    echo -e "${YELLOW}Warning: RAID state is not clean${NC}"
    mdadm --detail "$RAID_DEVICE"
fi

echo

# Create mount point if it doesn't exist
if [[ ! -d "$MOUNT_POINT" ]]; then
    echo -e "${YELLOW}Creating mount point: $MOUNT_POINT${NC}"
    mkdir -p "$MOUNT_POINT"
fi

# Mount the RAID array
echo -e "${YELLOW}Mounting RAID to $MOUNT_POINT...${NC}"
if mountpoint -q "$MOUNT_POINT"; then
    echo -e "${GREEN}✓ Already mounted${NC}"
else
    mount "$RAID_DEVICE" "$MOUNT_POINT"
    echo -e "${GREEN}✓ Mounted successfully${NC}"
fi

echo

# Display final status
echo -e "${YELLOW}RAID Status:${NC}"
mdadm --detail "$RAID_DEVICE" | grep -E "State|Raid Level|Array Size|Active Devices"

echo

echo -e "${GREEN}✓ RAID array ready for use at $MOUNT_POINT${NC}"
