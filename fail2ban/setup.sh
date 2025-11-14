#!/bin/bash
BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)
sudo apt install fail2ban rsyslog -y

cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 1d
findtime = 15m
maxretry = 3
backend = auto

[sshd]
port = 22

[nginx-http-auth]
enabled = true
mode    = aggressive
logpath = ${BASE_DIR}/nginx/log/error.log

[nginx-bad-request]
enabled = true
logpath = ${BASE_DIR}/nginx/log/access.log

[nginx-botsearch]
enabled = true
logpath = ${BASE_DIR}/nginx/log/access.log
EOF
