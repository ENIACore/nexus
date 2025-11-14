#!/bin/bash

#sudo certbot certonly --standalone --expand \
#  -d <domain> \

sudo certbot certonly --standalone --expand \
  -d nexus-alpha.myddns.me \
  -d api.nexus-alpha.myddns.me \
  -d demo.nexus-alpha.myddns.me \
  -d jelly.nexus-alpha.myddns.me \
  -d nextcloud.nexus-alpha.myddns.me \
  -d passwords.nexus-alpha.myddns.me \
  -d plex.nexus-alpha.myddns.me \
  -d www.nexus-alpha.myddns.me \
  -d vault.nexus-alpha.myddns.me
