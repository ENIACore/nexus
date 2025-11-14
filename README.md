
# Steps



- Format and flash USB drive with Ubunutu Server LTS using balenaEtcher
- Boot server from bootable flash drive and install ubuntu server
- Connect server to wifi using /etc/netscape/<someconfig>.yaml instructions found at https://linuxconfig.org/ubuntu-22-04-connect-to-wifi-from-command-line
- Go to router gateway (for ATT founda at http://192.168.1.254) and port forward 22, 443, 80880, and 80 to server (for ATT this is found at Firewall -> Nat/gaming)

1. Install Ubuntu
2. Connect to WiFi
3. Port forward via NAT in ATT gateway
4. Setup SSH for root (get key to server via USB)
5. Mount SSD (later will get revised to create RAID array)
6. Setup cloudflare dns
6. Setup dns cert
6. Start nginx with no sites enabled
6. Setup firewall
6. Setup ufw
7. Setup vaultwarden
8. Setup nextcloud
9. Setup jellyfin
10. Setup qbittorrent-nox + gluetun




## Gluetun setup
1. Go to [ProtonVPN WireGuard configuraiton page](https://account.proton.me/u/19/vpn/WireGuard) and generate a WG configuration
2. Copy the new WG private key into the gluetun.sh keys to enable gluetun VPN login
3. Run `gluetun/setup.sh` script to start gluetun VPN tunnel
4. Run `qbit/setup.sh` script to start qbittorrent-nox container behind gluetun
5. Copy `nginx/sites-available/qbit.lamkin` to `nginx/sites-enabled/qbit.lamkin` to enable reverse proxy access to qbittorrent's Web GUI 
