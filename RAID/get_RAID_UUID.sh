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
echo -e "${YELLOW}       Get RAID UUID                    ${NC}"
echo -e "${YELLOW}========================================${NC}"
echo

UUID=$(mdadm --detail /dev/md0 | grep UUID | awk '{print $NF}')
echo -e "UUID IS ${GREEN}${UUID}${NC}"
