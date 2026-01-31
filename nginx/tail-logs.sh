#!/bin/bash

# Tail nginx logs from Docker container
# Since logs are sent to syslog, we can view them via docker logs

CONTAINER_NAME="nexus-proxy"

# Check if container exists
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Error: Container '${CONTAINER_NAME}' not found"
    exit 1
fi

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Warning: Container '${CONTAINER_NAME}' is not running"
    echo "Showing logs from stopped container..."
fi

echo "Tailing logs for ${CONTAINER_NAME}..."
echo "Press Ctrl+C to stop"
echo "----------------------------------------"

# Follow docker logs (which receives syslog output)
docker logs -f --tail 100 ${CONTAINER_NAME}
