#!/bin/bash
# Docker volume management and backup

set -e

# Create named volume
docker volume create \
  --driver local \
  --opt type=none \
  --opt device=/path/on/host \
  --opt o=bind \
  app_data

# Create volume with specific options
docker volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw \
  --opt device=:/path/to/share \
  nfs_volume

# Backup volume to tar
backup_volume() {
    VOLUME_NAME=$1
    BACKUP_FILE="${VOLUME_NAME}_$(date +%Y%m%d_%H%M%S).tar.gz"

    echo "Backing up volume: $VOLUME_NAME"
    docker run --rm \
        -v ${VOLUME_NAME}:/data \
        -v $(pwd):/backup \
        alpine \
        tar czf /backup/${BACKUP_FILE} -C /data .

    echo "Backup saved to: ${BACKUP_FILE}"
}

# Restore volume from tar
restore_volume() {
    VOLUME_NAME=$1
    BACKUP_FILE=$2

    echo "Restoring volume: $VOLUME_NAME from $BACKUP_FILE"
    docker run --rm \
        -v ${VOLUME_NAME}:/data \
        -v $(pwd):/backup \
        alpine \
        sh -c "cd /data && tar xzf /backup/${BACKUP_FILE}"

    echo "Restore complete"
}

# Copy data between volumes
copy_volume() {
    SOURCE_VOLUME=$1
    DEST_VOLUME=$2

    echo "Copying from $SOURCE_VOLUME to $DEST_VOLUME"
    docker run --rm \
        -v ${SOURCE_VOLUME}:/source:ro \
        -v ${DEST_VOLUME}:/dest \
        alpine \
        sh -c "cp -av /source/. /dest/"
}

# List all volumes with size
echo "=== Docker Volumes ==="
docker volume ls

echo
echo "=== Volume Sizes ==="
docker system df -v | grep -A 20 "Local Volumes"

# Inspect volume
inspect_volume() {
    VOLUME_NAME=$1
    echo "=== Volume Details: $VOLUME_NAME ==="
    docker volume inspect $VOLUME_NAME
}

# Remove unused volumes
# docker volume prune -f

# Usage examples:
# backup_volume myvolume
# restore_volume myvolume backup.tar.gz
# copy_volume source_vol dest_vol
# inspect_volume myvolume
