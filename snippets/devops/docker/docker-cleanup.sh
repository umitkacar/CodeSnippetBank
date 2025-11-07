#!/bin/bash
# Docker system cleanup and optimization

set -e

echo "=== Docker Cleanup Script ==="
echo

# Stop all running containers (optional)
read -p "Stop all running containers? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping all containers..."
    docker stop $(docker ps -aq) 2>/dev/null || echo "No containers to stop"
fi

# Remove stopped containers
echo "Removing stopped containers..."
docker container prune -f

# Remove unused images
echo "Removing unused images..."
docker image prune -a -f

# Remove unused volumes
echo "Removing unused volumes..."
docker volume prune -f

# Remove unused networks
echo "Removing unused networks..."
docker network prune -f

# Remove build cache
echo "Removing build cache..."
docker buildx prune -f

# System prune with volumes
read -p "Perform full system prune with volumes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Performing full system prune..."
    docker system prune -a --volumes -f
fi

# Display disk usage
echo
echo "=== Current Docker Disk Usage ==="
docker system df

echo
echo "Cleanup complete!"
