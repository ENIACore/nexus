#!/bin/bash

# RAID Enclosure Safe Eject Script
# Usage: sudo ./raid_eject.sh

set -e  # Exit on any error

echo "=== RAID Enclosure Safe Eject ==="
echo "Timestamp: $(date)"
echo

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
   exit 1
fi

# Step 1: Check if RAID is mounted
echo "Step 1: Checking mount status..."
if mountpoint -q /mnt/RAID; then
    echo -e "${YELLOW}RAID is mounted. Checking for active processes...${NC}"
    
    # Check for processes using the mount point
    PROCESSES=$(lsof +D /mnt/RAID 2>/dev/null || true)
    if [[ -n "$PROCESSES" ]]; then
        echo -e "${RED}Warning: Processes are using the RAID mount:${NC}"
        echo "$PROCESSES"
        echo
        read -p "Kill these processes and continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborted by user."
            exit 1
        fi
        
        # Kill processes using the mount point
        echo "Killing processes..."
        fuser -km /mnt/RAID || true
        sleep 2
    fi
    
    # Sync filesystem
    echo "Syncing filesystem..."
    sync
    
    # Unmount
    echo "Unmounting /mnt/RAID..."
    umount /mnt/RAID
    
    # Verify unmount
    if mountpoint -q /mnt/RAID; then
        echo -e "${RED}Error: Failed to unmount /mnt/RAID${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Successfully unmounted /mnt/RAID${NC}"
else
    echo -e "${GREEN}✓ RAID is not mounted${NC}"
fi

# Step 2: Check RAID array status
echo
echo "Step 2: Checking RAID array status..."
if grep -q "md0" /proc/mdstat; then
    echo "RAID array md0 is active. Details:"
    mdadm --detail /dev/md0 --brief
    
    # Stop RAID array
    echo "Stopping RAID array..."
    mdadm --stop /dev/md0
    
    # Verify it's stopped
    if grep -q "md0" /proc/mdstat; then
        echo -e "${RED}Error: Failed to stop RAID array${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Successfully stopped RAID array${NC}"
else
    echo -e "${GREEN}✓ RAID array is not active${NC}"
fi

# Step 3: Power down drives
echo
echo "Step 3: Powering down drives..."

# Find RAID drives (look for 3.6T drives)
RAID_DRIVES=$(lsblk -rno NAME,SIZE | awk '$2 ~ /3\.6T/ {print "/dev/"$1}' | head -2)

if [[ -n "$RAID_DRIVES" ]]; then
    echo "Found RAID drives:"
    echo "$RAID_DRIVES"
    
    for drive in $RAID_DRIVES; do
        echo "Spinning down $drive..."
        hdparm -Y "$drive" 2>/dev/null || echo "  Warning: Could not spin down $drive"
    done
    
    echo -e "${GREEN}✓ Drives powered down${NC}"
else
    echo -e "${YELLOW}Warning: Could not identify RAID drives for power down${NC}"
fi

# Step 4: Final sync and wait
echo
echo "Step 4: Final system sync..."
sync
sleep 2

echo
echo -e "${GREEN}=== RAID Enclosure Ready for Safe Removal ===${NC}"
echo "You can now safely unplug your RAID enclosure."
echo "To remount after reconnecting, run: sudo ./raid_mount.sh"
echo
