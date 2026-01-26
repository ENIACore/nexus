#!/bin/bash

# RAID Enclosure Safe Mount Script
# Usage: sudo ./raid_mount.sh

set -e  # Exit on any error

echo "=== RAID Enclosure Safe Mount ==="
echo "Timestamp: $(date)"
echo

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
   exit 1
fi

# RAID configuration
RAID_UUID="6c1637c1:37578aa1:592c4e80:57f9b1de"
MOUNT_POINT="/mnt/RAID"

# Step 1: Wait for drive detection
echo "Step 1: Waiting for drive detection..."
sleep 3

# Check for drives
DETECTED_DRIVES=$(lsblk -rno NAME,SIZE | awk '$2 ~ /3\.6T/ {print "/dev/"$1"1"}' | head -2)
DRIVE_COUNT=$(echo "$DETECTED_DRIVES" | wc -l)

if [[ $DRIVE_COUNT -lt 2 ]] || [[ -z "$DETECTED_DRIVES" ]]; then
    echo -e "${RED}Error: Could not detect 2 RAID drives. Found:${NC}"
    lsblk | grep -E "3\.6T|sd[d-z]"
    echo
    echo "Please check connections and try again."
    exit 1
fi

echo -e "${GREEN}✓ Detected RAID drives:${NC}"
echo "$DETECTED_DRIVES"

# Step 2: Check RAID array status
echo
echo "Step 2: Checking RAID array status..."

# Check if array is already active
if grep -q "md0" /proc/mdstat; then
    echo -e "${YELLOW}RAID array md0 is already active:${NC}"
    cat /proc/mdstat | grep -A2 "md0"
    echo
    echo "Proceeding to mount check..."
else
    echo "RAID array not active. Attempting to assemble..."
    
    # Try auto-assembly first
    if mdadm --assemble --scan 2>/dev/null; then
        echo -e "${GREEN}✓ Auto-assembly successful${NC}"
    else
        echo "Auto-assembly failed. Trying manual assembly..."
        
        # Convert drive list to array for manual assembly
        DRIVE_ARRAY=($DETECTED_DRIVES)
        if [[ ${#DRIVE_ARRAY[@]} -ge 2 ]]; then
            echo "Assembling with drives: ${DRIVE_ARRAY[0]} ${DRIVE_ARRAY[1]}"
            mdadm --assemble /dev/md0 "${DRIVE_ARRAY[0]}" "${DRIVE_ARRAY[1]}"
            echo -e "${GREEN}✓ Manual assembly successful${NC}"
        else
            echo -e "${RED}Error: Not enough drives detected for manual assembly${NC}"
            exit 1
        fi
    fi
fi

# Step 3: Verify RAID health
echo
echo "Step 3: Verifying RAID health..."
if ! mdadm --detail /dev/md0 >/dev/null 2>&1; then
    echo -e "${RED}Error: RAID array /dev/md0 not accessible${NC}"
    exit 1
fi

RAID_STATE=$(mdadm --detail /dev/md0 | grep "State :" | awk '{print $3}')
echo "RAID State: $RAID_STATE"

if [[ "$RAID_STATE" != "clean" ]]; then
    echo -e "${YELLOW}Warning: RAID state is '$RAID_STATE' (not clean)${NC}"
    echo "RAID Details:"
    mdadm --detail /dev/md0
    echo
    read -p "Continue with mounting? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted by user."
        exit 1
    fi
else
    echo -e "${GREEN}✓ RAID array is healthy${NC}"
fi

# Step 4: Check filesystem
echo
echo "Step 4: Checking filesystem..."
if ! fsck -n /dev/md0 >/dev/null 2>&1; then
    echo -e "${YELLOW}Warning: Filesystem check reported issues${NC}"
    echo "Running read-only filesystem check:"
    fsck -n /dev/md0
    echo
    read -p "Continue with mounting? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted by user."
        exit 1
    fi
else
    echo -e "${GREEN}✓ Filesystem is clean${NC}"
fi

# Step 5: Create mount point if needed
echo
echo "Step 5: Preparing mount point..."
if [[ ! -d "$MOUNT_POINT" ]]; then
    echo "Creating mount point: $MOUNT_POINT"
    mkdir -p "$MOUNT_POINT"
fi

# Step 6: Mount the RAID
echo
echo "Step 6: Mounting RAID array..."

# Check if already mounted
if mountpoint -q "$MOUNT_POINT"; then
    echo -e "${GREEN}✓ RAID is already mounted at $MOUNT_POINT${NC}"
else
    echo "Mounting /dev/md0 to $MOUNT_POINT..."
    mount /dev/md0 "$MOUNT_POINT"
    
    # Verify mount
    if mountpoint -q "$MOUNT_POINT"; then
        echo -e "${GREEN}✓ Successfully mounted RAID${NC}"
    else
        echo -e "${RED}Error: Failed to mount RAID${NC}"
        exit 1
    fi
fi

# Step 7: Display final status
echo
echo -e "${BLUE}=== RAID Enclosure Successfully Mounted ===${NC}"
echo "Mount details:"
df -h | grep "$MOUNT_POINT"
echo
echo "RAID status:"
cat /proc/mdstat | grep -A2 "md0"
echo
echo "Contents:"
ls -la "$MOUNT_POINT"
echo
echo -e "${GREEN}Your RAID is ready for use!${NC}"
echo "To safely remove later, run: sudo ./raid_eject.sh"
echo
