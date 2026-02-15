#!/bin/bash
# Creates postrgres db for use by personal site and other sites
# Port 5432 is availble to containers on nexus network

sudo docker run --name nexus-pg \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -v postgres-dev:/var/lib/postgresql \
  -d postgres:latest
