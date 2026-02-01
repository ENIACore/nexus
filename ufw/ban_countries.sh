#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_UFW_ETC_DIR="${NEXUS_ETC_DIR}/ufw"
NEXUS_UFW_OPT_DIR="${NEXUS_OPT_DIR}/ufw"

print_header "BANNING FOREIGN COUNTRY CONNECTIONS"

# US IP Whitelist Script for UFW
# Allows only US IPs to access ports 22 (SSH), 80 (HTTP), and 443 (HTTPS)
set -e  # Exit on error

print_info "This will configure UFW to allow only US IPs on ports 22, 80, and 443"

# Verify files exist
if [ ! -f "us_ipv4.txt" ]; then
    print_error "ERROR: us_ipv4.txt not found!"
    exit 1
fi

if [ ! -f "us_ipv6.txt" ]; then
    print_error "ERROR: us_ipv6.txt not found!"
    exit 1
fi

# Count total rules that will be created
ipv4_count=$(wc -l < us_ipv4.txt)
ipv6_count=$(wc -l < us_ipv6.txt)
total_rules=$(( ($ipv4_count + $ipv6_count) * 3 ))

print_info "IPv4 ranges: $ipv4_count"
print_info "IPv6 ranges: $ipv6_count"
print_info "Total rules to create: $total_rules (this will take a while)"
print_info ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

print_step "Step 1: Setting default policies..."
ufw default deny incoming
ufw default allow outgoing

print_step "Step 2: Adding IPv4 rules for port 22 (SSH)..."
while read line; do 
    [ -z "$line" ] && continue
    ufw allow from "$line" to any port 22 proto tcp
done < us_ipv4.txt

print_step "Step 3: Adding IPv4 rules for port 80 (HTTP)..."
while read line; do 
    [ -z "$line" ] && continue
    ufw allow from "$line" to any port 80 proto tcp
done < us_ipv4.txt

print_step "Step 4: Adding IPv4 rules for port 443 (HTTPS)..."
while read line; do 
    [ -z "$line" ] && continue
    ufw allow from "$line" to any port 443 proto tcp
done < us_ipv4.txt

print_step "Step 5: Adding IPv6 rules for port 22 (SSH)..."
while read line; do 
    [ -z "$line" ] && continue
    ufw allow from "$line" to any port 22 proto tcp
done < us_ipv6.txt

print_step "Step 6: Adding IPv6 rules for port 80 (HTTP)..."
while read line; do 
    [ -z "$line" ] && continue
    ufw allow from "$line" to any port 80 proto tcp
done < us_ipv6.txt

print_step "Step 7: Adding IPv6 rules for port 443 (HTTPS)..."
while read line; do 
    [ -z "$line" ] && continue
    ufw allow from "$line" to any port 443 proto tcp
done < us_ipv6.txt

print_success "Configuration Complete"
print_info "Review the rules with: ufw status numbered"
read -p "Enable UFW firewall now? (yes/no): " enable_choice

if [ "$enable_choice" = "yes" ]; then
    print_info "Enabling UFW..."
    ufw enable
    print_info ""
    print_info "UFW is now active!"
    ufw status verbose
else
    print_info "UFW not enabled. Enable manually with: sudo ufw enable"
fi
