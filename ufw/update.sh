#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_UFW_ETC_DIR="${NEXUS_ETC_DIR}/ufw"
NEXUS_UFW_OPT_DIR="${NEXUS_OPT_DIR}/ufw"

print_header "CONFIGURING UFW FIREWALL FOR NEXUS"

# Installing required packages
print_step "Installing required packages"
if sudo apt install iptables ipset ufw cron curl wget rsyslog -y; then
    print_info "Required packages installed successfully"
else
    print_error "Failed to install required packages"
    exit 1
fi

# Creating UFW configuration directory
print_step "Creating UFW configuration directory at ${NEXUS_UFW_ETC_DIR}"
mkdir -p "${NEXUS_UFW_ETC_DIR}"

# Configure UFW rules
print_step "Configuring UFW rules"
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH, HTTP, and HTTPS
print_step "Allowing SSH, HTTP, and HTTPS"
sudo ufw allow 22/tcp comment "OpenSSH"
sudo ufw allow 80/tcp comment "HTTP"
sudo ufw allow 443/tcp comment "HTTPS"

# Download and setup blocklist script
print_step "Setting up IP blocklist updater"
sudo wget -q https://gist.githubusercontent.com/arter97/2b71e193700ab002c75d1e5a0e7da6dc/raw/firewall.sh -O "${NEXUS_UFW_ETC_DIR}/blocklist.sh"
sudo chmod 755 "${NEXUS_UFW_ETC_DIR}/blocklist.sh"
sudo chmod +x "${NEXUS_UFW_ETC_DIR}/blocklist.sh"

# Run initial blocklist update
print_step "Running initial IP blocklist update"
if sudo "${NEXUS_UFW_ETC_DIR}/blocklist.sh"; then
    print_info "IP blocklist updated successfully"
else
    print_warning "Failed to update IP blocklist, continuing anyway"
fi

# Enable UFW
print_step "Enabling UFW firewall"
if sudo ufw --force enable; then
    print_success "UFW firewall configured and enabled successfully"
    print_info ""
    print_info "Next steps:"
    print_info "1. Run ${NEXUS_UFW_OPT_DIR}/schedule.sh to set up automatic blocklist updates"
    print_info "2. Use 'sudo ufw status' to view current firewall rules"
    print_info "3. Run ${NEXUS_UFW_OPT_DIR}/update.sh to manually update the IP blocklist"
else
    print_error "Failed to enable UFW firewall"
    exit 1
fi
