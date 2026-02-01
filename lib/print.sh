#!/bin/bash
# Colored output functions for Nexus scripts - /opt/nexus/lib/print.sh

# Colors
RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
BLUE='\033[94m'
MAGENTA='\033[95m'
CYAN='\033[96m'
WHITE='\033[97m'
RESET='\033[0m'
BOLD='\033[1m'

print_error() {
    echo -e "${RED}${BOLD}[ERROR]${RESET} ${RED}$1${RESET}"
}

print_success() {
    echo -e "${GREEN}${BOLD}[SUCCESS]${RESET} ${GREEN}$1${RESET}"
}

print_warning() {
    echo -e "${YELLOW}${BOLD}[WARNING]${RESET} ${YELLOW}$1${RESET}"
}

print_info() {
    echo -e "${BLUE}${BOLD}[INFO]${RESET} ${BLUE}$1${RESET}"
}

print_step() {
    echo -e "${CYAN}${BOLD}[STEP]${RESET} ${CYAN}$1${RESET}"
}

print_header() {
    local line
    line=$(printf '=%.0s' {1..60})
    echo -e "\n${MAGENTA}${BOLD}${line}${RESET}"
    printf "${MAGENTA}${BOLD}%*s${RESET}\n" $(((${#1}+60)/2)) "$1"
    echo -e "${MAGENTA}${BOLD}${line}${RESET}\n"
}
