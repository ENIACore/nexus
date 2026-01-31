#!/bin/bash

# !Prior to running script
# Add cloudlare.ini file to /nexus/keys/ with API Key `dns_cloudflare_api_token = <token>`
# Chmod 600 cloudflare.ini

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)
CF_API_KEY="${BASE_DIR}/keys/cloudflare.ini"

sudo certbot certonly \
  --dns-cloudflare \
  --dns-cloudflare-credentials "${CF_API_KEY}" \
  --dns-cloudflare-propagation-seconds 60 \
  -d "*.lamkin.dev" \
  -d "lamkin.dev"

sleep 1

echo "Verifying certbot renewal timer is working"
sudo systemctl status certbot.timer

echo "Verifying certbot renewal functions"
sudo certbot renew --dry-run
