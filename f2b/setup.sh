#!/bin/bash
source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_F2B_ETC_DIR="${NEXUS_ETC_DIR}/f2b"
NEXUS_F2B_OPT_DIR="${NEXUS_OPT_DIR}/f2b"
NEXUS_NGINX_LOG_DIR="${NEXUS_LOG_DIR}/nginx"

print_header "CONFIGURING FAIL2BAN FOR NEXUS NGINX"

# Ensuring nginx log directory exists
require_dir "${NEXUS_NGINX_LOG_DIR}" "Nginx log directory for fail2ban monitoring"

# Installing fail2ban
print_step "Installing fail2ban"
if ! command -v fail2ban-client &> /dev/null; then
    sudo apt update && sudo apt install fail2ban -y
else
    print_info "fail2ban already installed"
fi

# Creating fail2ban configuration directory
print_step "Creating fail2ban configuration directory at ${NEXUS_F2B_ETC_DIR}"
mkdir -p "${NEXUS_F2B_ETC_DIR}"

# Generating jail.local with environment variables
print_step "Generating jail.local configuration"
cat > "${NEXUS_F2B_OPT_DIR}/jail.local" << EOF
[DEFAULT]
bantime = 1d
findtime = 15m
maxretry = 3
banaction = ufw

[sshd]
enabled = true
port = 22

[nginx-http-auth]
enabled = true
mode = aggressive
logpath = ${NEXUS_NGINX_LOG_DIR}/access.log
          ${NEXUS_NGINX_LOG_DIR}/error.log

[nginx-bad-request]
enabled = true
logpath = ${NEXUS_NGINX_LOG_DIR}/access.log
          ${NEXUS_NGINX_LOG_DIR}/error.log

[nginx-botsearch]
enabled = true
logpath = ${NEXUS_NGINX_LOG_DIR}/access.log

[nginx-limit-req]
enabled = true
logpath = ${NEXUS_NGINX_LOG_DIR}/error.log
EOF

# Copying latest jail.local file to fail2ban config directory
print_step "Copying latest jail.local to ${NEXUS_F2B_ETC_DIR}"
cp "${NEXUS_F2B_OPT_DIR}/jail.local" "${NEXUS_F2B_ETC_DIR}/jail.local"

# Creating symlink to system fail2ban directory
print_step "Creating symlink to system fail2ban configuration"
sudo ln -sf "${NEXUS_F2B_ETC_DIR}/jail.local" /etc/fail2ban/jail.local

# Restarting and enabling fail2ban
print_step "Restarting fail2ban service"
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

if [ $? -eq 0 ]; then
    print_info "Active jails can be checked with: sudo fail2ban-client status"
    print_info "To update configuration:"
    print_info "1. Edit ${NEXUS_F2B_ETC_DIR}/jail.local"
    print_info "2. Run ${NEXUS_F2B_OPT_DIR}/reload.sh to apply changes"
    print_info ""
    print_success "fail2ban configured successfully"
else
    print_error "Failed to configure fail2ban"
    exit 1
fi
