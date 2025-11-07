#!/bin/bash
# Docker build with BuildKit and advanced caching

set -e

IMAGE_NAME="${1:-myapp}"
IMAGE_TAG="${2:-latest}"
CACHE_REPO="${3:-ghcr.io/myorg/cache}"

# Enable BuildKit
export DOCKER_BUILDKIT=1

echo "Building ${IMAGE_NAME}:${IMAGE_TAG} with cache optimization..."

# Build with inline cache and multiple cache sources
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --cache-from type=registry,ref=${CACHE_REPO}:buildcache \
  --cache-to type=registry,ref=${CACHE_REPO}:buildcache,mode=max \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  --build-arg VERSION=${IMAGE_TAG} \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VCS_REF=$(git rev-parse --short HEAD) \
  --label org.opencontainers.image.created=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --label org.opencontainers.image.version=${IMAGE_TAG} \
  --label org.opencontainers.image.revision=$(git rev-parse HEAD) \
  --tag ${IMAGE_NAME}:${IMAGE_TAG} \
  --tag ${IMAGE_NAME}:latest \
  --push \
  --progress=plain \
  .

echo "Build completed successfully!"

# Optionally scan for vulnerabilities
if command -v trivy &> /dev/null; then
    echo "Scanning image for vulnerabilities..."
    trivy image --severity HIGH,CRITICAL ${IMAGE_NAME}:${IMAGE_TAG}
fi
