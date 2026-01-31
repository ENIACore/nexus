#!/bin/bash
# Creates a dedicated nexus system user for running services and cron jobs

USER_NAME="nexus"
USER_COMMENT="Nexus service user"

# Check if user already exists
if id "${USER_NAME}" &>/dev/null; then
    echo "User '${USER_NAME}' already exists"
    exit 0
fi

echo "Creating system user '${USER_NAME}'..."

# Create system user without home directory, no login shell
sudo useradd \
    --system \
    --no-create-home \
    --shell /usr/sbin/nologin \
    --comment "${USER_COMMENT}" \
    "${USER_NAME}"

if [[ $? -eq 0 ]]; then
    echo "SUCCESS: System user '${USER_NAME}' created"
    id "${USER_NAME}"
else
    echo "ERROR: Failed to create user '${USER_NAME}'"
    exit 1
fi
