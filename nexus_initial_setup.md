

## Gluetun setup
1. Go to [ProtonVPN WireGuard configuraiton page](https://account.proton.me/u/19/vpn/WireGuard) and generate a WG configuration
2. Copy the new WG private key into the gluetun.sh keys to enable gluetun VPN login
3. Run `gluetun/setup.sh` script to start gluetun VPN tunnel
4. Run `qbit/setup.sh` script to start qbittorrent-nox container behind gluetun
5. Copy `nginx/sites-available/qbit.lamkin` to `nginx/sites-enabled/qbit.lamkin` to enable reverse proxy access to qbittorrent's Web GUI 
