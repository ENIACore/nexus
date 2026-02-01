#!/bin/bash
source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"

NEXUS_F2B_ETC_DIR="${NEXUS_ETC_DIR}/f2b"
NEXUS_F2B_OPT_DIR="${NEXUS_OPT_DIR}/f2b"

# Ensuring jail.local exists
require_file "${NEXUS_F2B_OPT_DIR}/jail.local" "fail2ban configuration file"

print_header "RELOADING FAIL2BAN"

# Copying latest jail.local file to fail2ban config directory
print_step "Copying latest jail.local to ${NEXUS_F2B_ETC_DIR}"
cp "${NEXUS_F2B_OPT_DIR}/jail.local" "${NEXUS_F2B_ETC_DIR}/jail.local"

# Creating symlink to system fail2ban directory with latest config
print_step "Ensuring symlink to system fail2ban configuration"
sudo ln -sf "${NEXUS_F2B_ETC_DIR}/jail.local" /etc/fail2ban/jail.local

print_step "Restarting fail2ban service"
sudo systemctl restart fail2ban

if [ $? -eq 0 ]; then
    print_success "fail2ban reloaded successfully"
    
    # Wait for fail2ban to be fully ready
    print_step "Waiting for fail2ban to be ready"
    for i in {1..10}; do
        if sudo fail2ban-client ping &>/dev/null; then
            sudo fail2ban-client status
            exit 0
        fi
        sleep 1
    done
    
    print_error "fail2ban started but socket not ready after 10 seconds"
    exit 1
else
    print_error "Failed to reload fail2ban"
    exit 1
fi
