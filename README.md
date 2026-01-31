# Nexus Server Installation

## Quick Install

Run this command in your Ubuntu terminal to start the installation:
```bash
curl -fsSL https://raw.githubusercontent.com/ENIACore/nexus/main/install.py -o /tmp/nexus-install.py && sudo python3 /tmp/nexus-install.py; rm -f /tmp/nexus-install.py
```

## Requirements

- Ubuntu Server LTS
- Root/sudo access
- Internet connection

## What Gets Installed

- Nextcloud
- Vaultwarden
- Jellyfin
- qBittorrent + Gluetun VPN
- Nginx reverse proxy
- Cloudflare DNS & SSL
- Fail2ban
- UFW firewall
