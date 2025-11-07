#!/bin/bash
# Comprehensive Docker image security scanning

set -e

IMAGE="${1}"

if [ -z "$IMAGE" ]; then
    echo "Usage: $0 <image:tag>"
    exit 1
fi

echo "=== Docker Image Security Scan ==="
echo "Image: $IMAGE"
echo

# Check if image exists
if ! docker image inspect "$IMAGE" &>/dev/null; then
    echo "Error: Image $IMAGE not found"
    exit 1
fi

# Trivy vulnerability scan
if command -v trivy &> /dev/null; then
    echo "--- Trivy Vulnerability Scan ---"
    trivy image --severity HIGH,CRITICAL "$IMAGE"
    echo
else
    echo "Warning: trivy not installed"
fi

# Grype vulnerability scan
if command -v grype &> /dev/null; then
    echo "--- Grype Vulnerability Scan ---"
    grype "$IMAGE" --fail-on critical
    echo
else
    echo "Warning: grype not installed"
fi

# Docker bench security
if command -v docker-bench-security &> /dev/null; then
    echo "--- Docker Bench Security ---"
    docker-bench-security
    echo
fi

# Check for non-root user
echo "--- User Check ---"
USER_INFO=$(docker image inspect "$IMAGE" --format '{{.Config.User}}')
if [ -z "$USER_INFO" ] || [ "$USER_INFO" = "root" ] || [ "$USER_INFO" = "0" ]; then
    echo "WARNING: Image runs as root user!"
else
    echo "OK: Image runs as user: $USER_INFO"
fi
echo

# Check image size
echo "--- Image Size ---"
SIZE=$(docker image inspect "$IMAGE" --format '{{.Size}}' | awk '{print $1/1024/1024 " MB"}')
echo "Image size: $SIZE"
echo

# List exposed ports
echo "--- Exposed Ports ---"
docker image inspect "$IMAGE" --format '{{range $p, $conf := .Config.ExposedPorts}}{{$p}} {{end}}'
echo

# Check for secrets in image
echo "--- Secrets Detection ---"
docker history --no-trunc "$IMAGE" | grep -iE 'password|secret|key|token' || echo "No obvious secrets found"
echo

echo "=== Security Scan Complete ==="
