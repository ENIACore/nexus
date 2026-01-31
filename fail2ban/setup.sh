#!/bin/bash
BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)

# Install fail2ban and rsyslog
sudo apt install fail2ban rsyslog -y

# Configure fail2ban to read nginx logs from syslog
# Nginx logs are sent to syslog via Docker logging driver with tag 'nginx/nexus-proxy'
sudo tee /etc/fail2ban/jail.local > /dev/null << 'EOF'
[DEFAULT]
bantime = 1d
findtime = 15m
maxretry = 3
backend = systemd
banaction = ufw

[sshd]
enabled = true
port = 22

[nginx-http-auth]
enabled = true
mode = aggressive
logpath = /var/log/syslog
filter = nginx-http-auth

[nginx-bad-request]
enabled = true
logpath = /var/log/syslog
filter = nginx-bad-request

[nginx-botsearch]
enabled = true
logpath = /var/log/syslog
filter = nginx-botsearch

[nginx-limit-req]
enabled = true
logpath = /var/log/syslog
filter = nginx-limit-req
EOF

# Restart fail2ban to apply changes
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

echo "fail2ban configured to read nginx logs from /var/log/syslog"
echo "Run 'sudo fail2ban-client status' to check active jails"
