#!/bin/bash
# RAID Recovery Script - Interactive Version

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}       RAID Recovery Script${NC}"
echo -e "${YELLOW}========================================${NC}"
echo

# Default values
DEFAULT_ARRAY="/dev/md0"
DEFAULT_MOUNT="/mnt/RAID"

# Get array device
read -p "Enter RAID array device [${DEFAULT_ARRAY}]: " ARRAY
ARRAY=${ARRAY:-$DEFAULT_ARRAY}

# Get mount point
read -p "Enter mount point [${DEFAULT_MOUNT}]: " MOUNT_POINT
MOUNT_POINT=${MOUNT_POINT:-$DEFAULT_MOUNT}

# Show available partitions that might be RAID members
echo
echo -e "${YELLOW}Available partitions:${NC}"
lsblk -o NAME,SIZE,TYPE,FSTYPE | grep -E "disk|part"
echo

# Get first drive
read -p "Enter first RAID member partition (e.g., sdc1): " DRIVE1
if [[ ! "$DRIVE1" =~ ^/dev/ ]]; then
    DRIVE1="/dev/${DRIVE1}"
fi

# Get second drive
read -p "Enter second RAID member partition (e.g., sdd1): " DRIVE2
if [[ ! "$DRIVE2" =~ ^/dev/ ]]; then
    DRIVE2="/dev/${DRIVE2}"
fi

# Validate drives exist
echo
echo -e "${YELLOW}Validating drives...${NC}"
for drive in "$DRIVE1" "$DRIVE2"; do
    if [[ ! -b "$drive" ]]; then
        echo -e "${RED}Error: $drive does not exist${NC}"
        exit 1
    fi
done
echo -e "${GREEN}Both drives exist${NC}"

# Show RAID info from drives
echo
echo -e "${YELLOW}RAID information from drives:${NC}"
echo "--- ${DRIVE1} ---"
mdadm --examine "$DRIVE1" 2>/dev/null | grep -E "Array UUID|Array State|Update Time|Events" || echo "Could not examine drive"
echo "--- ${DRIVE2} ---"
mdadm --examine "$DRIVE2" 2>/dev/null | grep -E "Array UUID|Array State|Update Time|Events" || echo "Could not examine drive"

# Summary and confirmation
echo
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Summary of actions:${NC}"
echo -e "${YELLOW}========================================${NC}"
echo "1. Unmount ${MOUNT_POINT}"
echo "2. Stop array ${ARRAY}"
echo "3. Reassemble ${ARRAY} with ${DRIVE1} and ${DRIVE2}"
echo "4. Mount ${ARRAY} to ${MOUNT_POINT}"
echo
echo -e "${RED}WARNING: Make sure you have selected the correct drives!${NC}"
read -p "Proceed with recovery? (yes/no): " CONFIRM

if [[ "$CONFIRM" != "yes" ]]; then
    echo "Aborted."
    exit 0
fi

# Execute recovery
echo
echo -e "${YELLOW}Starting recovery...${NC}"

# Step 1: Unmount
echo -n "Unmounting ${MOUNT_POINT}... "
if mountpoint -q "$MOUNT_POINT" 2>/dev/null; then
    if umount "$MOUNT_POINT" 2>/dev/null; then
        echo -e "${GREEN}done${NC}"
    else
        echo -e "${YELLOW}failed (may not be mounted)${NC}"
    fi
else
    echo -e "${YELLOW}not mounted${NC}"
fi

# Step 2: Stop array
echo -n "Stopping ${ARRAY}... "
if mdadm --stop "$ARRAY" 2>/dev/null; then
    echo -e "${GREEN}done${NC}"
else
    echo -e "${YELLOW}failed (may already be stopped)${NC}"
fi

# Step 3: Reassemble
echo -n "Reassembling ${ARRAY}... "
if mdadm --assemble "$ARRAY" "$DRIVE1" "$DRIVE2"; then
    echo -e "${GREEN}done${NC}"
else
    echo -e "${RED}failed${NC}"
    echo "Attempting forced assembly..."
    mdadm --assemble --force "$ARRAY" "$DRIVE1" "$DRIVE2"
fi

# Step 4: Mount
echo -n "Mounting ${ARRAY} to ${MOUNT_POINT}... "
if mount "$ARRAY" "$MOUNT_POINT"; then
    echo -e "${GREEN}done${NC}"
else
    echo -e "${RED}failed${NC}"
    exit 1
fi

# Show result
echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Recovery complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo "Array status:"
mdadm --detail "$ARRAY" | grep -E "State|Active|Working|Failed"
echo
echo "Mount status:"
df -h "$MOUNT_POINT"
