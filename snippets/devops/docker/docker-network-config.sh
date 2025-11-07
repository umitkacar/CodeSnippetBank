#!/bin/bash
# Docker network configuration and management

set -e

# Create custom bridge network with specific subnet
docker network create \
  --driver bridge \
  --subnet=172.20.0.0/16 \
  --ip-range=172.20.240.0/20 \
  --gateway=172.20.0.1 \
  --opt "com.docker.network.bridge.name"="docker_bridge" \
  --opt "com.docker.network.bridge.enable_ip_masquerade"="true" \
  --opt "com.docker.network.bridge.enable_icc"="true" \
  --opt "com.docker.network.driver.mtu"="1500" \
  custom_network

# Create overlay network for swarm
docker network create \
  --driver overlay \
  --subnet=10.0.9.0/24 \
  --attachable \
  overlay_network

# Create macvlan network
docker network create \
  --driver macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  --opt parent=eth0 \
  macvlan_network

# Create internal network (no external access)
docker network create \
  --driver bridge \
  --internal \
  internal_network

# List all networks
echo "=== Docker Networks ==="
docker network ls

# Inspect network
echo
echo "=== Custom Network Details ==="
docker network inspect custom_network

# Connect container to network
# docker network connect custom_network container_name

# Disconnect container from network
# docker network disconnect custom_network container_name

# Clean up unused networks
# docker network prune -f
