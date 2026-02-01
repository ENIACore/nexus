#!/bin/bash

if docker exec nexus-proxy nginx -s reload; then
    print_info "Nginx reloaded successfully"
else
    print_error "Failed to reload nginx"
    exit 1
fi
