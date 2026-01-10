#!/bin/bash
# Sets up gluetun in specific order and timing for dependencies (currently, to enable gluetun and qbittorrent API connection)

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)
GLUETUN_SETUP="${BASE_DIR}/gluetun/setup.sh"
QBIT_SETUP="${BASE_DIR}/qbit/setup.sh"

source "${GLUETUN_SETUP}"

# Allow gluetun to properly setup
sleep 2

source "${QBIT_SETUP}"
