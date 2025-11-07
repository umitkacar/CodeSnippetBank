#!/bin/bash
# Docker image size optimization and analysis

set -e

IMAGE="${1}"

if [ -z "$IMAGE" ]; then
    echo "Usage: $0 <image:tag>"
    exit 1
fi

echo "=== Docker Image Optimization Analysis ==="
echo "Image: $IMAGE"
echo

# Show image size
echo "--- Image Size ---"
docker images "$IMAGE" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
echo

# Analyze layers
echo "--- Layer Analysis ---"
docker history "$IMAGE" --no-trunc --format "table {{.CreatedBy}}\t{{.Size}}"
echo

# Show detailed layer information
echo "--- Top 10 Largest Layers ---"
docker history "$IMAGE" --format "{{.Size}}\t{{.CreatedBy}}" | \
    grep -v "0B" | \
    sort -rh | \
    head -10
echo

# Use dive for detailed analysis (if installed)
if command -v dive &> /dev/null; then
    echo "--- Detailed Layer Analysis (dive) ---"
    dive "$IMAGE" --ci
else
    echo "Tip: Install 'dive' for detailed layer analysis"
    echo "  https://github.com/wagoodman/dive"
fi

# Optimization suggestions
echo
echo "=== Optimization Suggestions ==="
echo "1. Use multi-stage builds to reduce final image size"
echo "2. Combine RUN commands to reduce layers"
echo "3. Use .dockerignore to exclude unnecessary files"
echo "4. Clean package manager caches (apt-get clean, npm cache clean)"
echo "5. Use Alpine-based images when possible"
echo "6. Remove development dependencies in production builds"
echo "7. Use COPY instead of ADD when possible"
echo "8. Order Dockerfile commands from least to most frequently changing"
