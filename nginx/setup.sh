#!/bin/bash

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)

# Create the network first (if it doesn't exist)
docker network create nexus

# Run nginx container
docker run -d \
    --name nexus-proxy \
    --restart unless-stopped \
    --network nexus \
    -p 80:80 \
    -p 443:443 \
    --read-only \
    -v ${BASE_DIR}/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
    -v ${BASE_DIR}/nginx/conf.d:/etc/nginx/conf.d:ro \
    -v ${BASE_DIR}/nginx/sites-enabled:/etc/nginx/sites-enabled:ro \
    -v ${BASE_DIR}/nginx/snippets:/etc/nginx/snippets:ro \
    -v ${BASE_DIR}/nginx/log:/var/log/nginx \
    -v ${BASE_DIR}/nginx/cache:/var/cache/nginx \
    -v ${BASE_DIR}/nginx/pid:/var/run \
    -v /etc/letsencrypt:/etc/letsencrypt:ro \
    -v ${BASE_DIR}/nginx/www:/var/www:ro \
    --health-cmd="nginx -t && curl -f http://localhost/ || exit 1" \
    --health-interval=30s \
    --health-timeout=3s \
    --health-retries=3 \
    --health-start-period=30s \
    nginx:latest
