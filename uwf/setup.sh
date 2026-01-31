#!/bin/bash

#Create firewall
sudo apt install iptables ipset ufw cron curl wget rsyslog -y

#Allow SSH, HTTP, and HTTPS
sudo ufw allow 22/tcp comment "OpenSSH"
sudo ufw allow 80/tcp comment "HTTP"
sudo ufw allow 443/tcp comment "HTTPS"

sudo wget https://gist.githubusercontent.com/arter97/2b71e193700ab002c75d1e5a0e7da6dc/raw/firewall.sh -O /opt/firewall.sh
sudo chmod 755 /opt/firewall.sh
sudo /opt/firewall.sh
