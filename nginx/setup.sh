#!/bin/bash

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)

# Ensure docker network exists
if ! docker network inspect nexus >/dev/null 2>&1; then
  docker network create nexus >/dev/null
fi

# Run nginx container with standard directory structure
# - Config files: mounted read-only from host
# - Working directories (cache, pid, logs): tmpfs or container-managed
# - Logs: sent to syslog via Docker logging driver
docker run -d \
    --name nexus-proxy \
    --restart unless-stopped \
    --network nexus \
    -p 80:80 \
    -p 443:443 \
    --read-only \
    --log-driver syslog \
    --log-opt syslog-address=unixgram:///dev/log \
    --log-opt tag="nginx/{{.Name}}" \
    --log-opt syslog-format=rfc5424 \
    -v ${BASE_DIR}/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
    -v ${BASE_DIR}/nginx/conf.d:/etc/nginx/conf.d:ro \
    -v ${BASE_DIR}/nginx/sites-enabled:/etc/nginx/sites-enabled:ro \
    -v ${BASE_DIR}/nginx/snippets:/etc/nginx/snippets:ro \
    -v /etc/letsencrypt:/etc/letsencrypt:ro \
    -v ${BASE_DIR}/nginx/www:/var/www:ro \
    --tmpfs /var/cache/nginx:rw,noexec,nosuid,size=100m \
    --tmpfs /var/run:rw,noexec,nosuid,size=10m \
    --tmpfs /var/log/nginx:rw,noexec,nosuid,size=50m \
    --health-cmd="nginx -t && curl -f http://localhost/ || exit 1" \
    --health-interval=30s \
    --health-timeout=3s \
    --health-retries=3 \
    --health-start-period=30s \
    nginx:latest
