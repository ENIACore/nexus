#!/bin/bash

# Setup script for Nextcloud directories and permissions
echo "Setting up Nextcloud directory structure..."

# Create the main directory structure
sudo mkdir -p /opt/nextcloud/{html,data,config,custom_apps,themes,db,redis}

# Set proper ownership (33 is the www-data user ID in the container)
echo "Setting proper ownership..."
sudo chown -R 33:33 /opt/nextcloud/html
sudo chown -R 33:33 /opt/nextcloud/data
sudo chown -R 33:33 /opt/nextcloud/config
sudo chown -R 33:33 /opt/nextcloud/custom_apps
sudo chown -R 33:33 /opt/nextcloud/themes

# Set ownership for database (999 is the mysql user ID in MariaDB container)
sudo chown -R 999:999 /opt/nextcloud/db

# Set ownership for Redis (999 is the redis user ID in Redis container)
sudo chown -R 999:999 /opt/nextcloud/redis

# Set proper permissions
echo "Setting proper permissions..."
sudo chmod -R 755 /opt/nextcloud/html
sudo chmod -R 750 /opt/nextcloud/data
sudo chmod -R 750 /opt/nextcloud/config

echo "Directory structure created successfully!"
echo ""
echo "Directory structure:"
echo "/opt/nextcloud/"
echo "├── html/           # Main Nextcloud installation"
echo "├── data/           # User files and uploads"
echo "├── config/         # Configuration files"
echo "├── custom_apps/    # Custom/additional apps"
echo "├── themes/         # Custom themes"
echo "├── db/             # MariaDB database files"
echo "└── redis/          # Redis cache data"
echo ""
echo "IMPORTANT: Before running docker-compose up, make sure to:"
echo "1. Replace all password placeholders in docker-compose.yml"
echo "2. Update the trusted domains if needed"
echo "3. Ensure your reverse proxy is properly configured"
