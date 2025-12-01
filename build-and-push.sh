#!/bin/bash

# Sonarr-Radarr MCP - Build and Push Script for Multi-Architecture Images
# Builds for both linux/amd64 and linux/arm64
# Supports both Docker and Podman
# Usage: ./build-and-push.sh [version] [github-username]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VERSION="${1}"
GITHUB_USERNAME="${2:-${GITHUB_USERNAME}}"
IMAGE_NAME="mcp-servarr"
REGISTRY="ghcr.io"
PLATFORMS="linux/amd64,linux/arm64"

# Validation
if [ -z "$VERSION" ]; then
    echo -e "${RED}Error: Version not specified${NC}"
    echo "Usage: $0 <version> [github-username]"
    echo "Example: $0 0.1 myusername"
    exit 1
fi

if [ -z "$GITHUB_USERNAME" ]; then
    echo -e "${RED}Error: GitHub username not specified${NC}"
    echo "Usage: $0 <version> <github-username>"
    echo "Or set GITHUB_USERNAME environment variable"
    exit 1
fi

# Detect container tool (docker or podman)
CONTAINER_TOOL=""
if command -v docker &> /dev/null; then
    CONTAINER_TOOL="docker"
    echo -e "${GREEN}✓${NC} Using Docker"
elif command -v podman &> /dev/null; then
    CONTAINER_TOOL="podman"
    echo -e "${GREEN}✓${NC} Using Podman"
else
    echo -e "${RED}Error: Neither docker nor podman is installed${NC}"
    exit 1
fi

# Check if logged in to ghcr.io
if ! $CONTAINER_TOOL login ghcr.io --get-login &> /dev/null; then
    echo -e "${YELLOW}Warning: Not logged in to ghcr.io${NC}"
    echo "Please login first:"
    echo "  echo \$GITHUB_TOKEN | $CONTAINER_TOOL login ghcr.io -u $GITHUB_USERNAME --password-stdin"
    exit 1
fi

# Setup multi-architecture build support
if [ "$CONTAINER_TOOL" = "docker" ]; then
    # Check if buildx is available
    if ! docker buildx version &> /dev/null; then
        echo -e "${RED}Error: docker buildx is not available${NC}"
        echo "Please install Docker Desktop or enable buildx plugin"
        exit 1
    fi

    # Create or use existing buildx builder for multi-platform builds
    if ! docker buildx ls | grep -q multiarch-builder; then
        echo -e "${GREEN}➤${NC} Creating buildx builder for multi-platform builds..."
        docker buildx create --name multiarch-builder --driver docker-container --use
    else
        echo -e "${GREEN}➤${NC} Using existing multiarch-builder..."
        docker buildx use multiarch-builder
    fi

    # Bootstrap the builder
    docker buildx inspect --bootstrap
fi

IMAGE_FULL="${REGISTRY}/${GITHUB_USERNAME}/${IMAGE_NAME}"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}Building Multi-Architecture Container Image${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo "Image: ${IMAGE_FULL}"
echo "Version: ${VERSION}"
echo "Platforms: ${PLATFORMS}"
echo "Tool: ${CONTAINER_TOOL}"
echo ""

# Build the multi-architecture image
if [ "$CONTAINER_TOOL" = "docker" ]; then
    # Docker buildx multi-platform build
    echo -e "${GREEN}➤${NC} Building multi-arch image with Docker buildx..."
    docker buildx build \
      --platform ${PLATFORMS} \
      -t ${IMAGE_FULL}:${VERSION} \
      -t ${IMAGE_FULL}:latest \
      --load \
      .

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Build failed${NC}"
        exit 1
    fi
else
    # Podman manifest-based multi-platform build
    echo -e "${GREEN}➤${NC} Building multi-arch image with Podman manifest..."

    # Clean up any existing manifests to avoid conflicts
    echo -e "${GREEN}  ➤${NC} Cleaning up old manifests..."
    podman manifest rm ${IMAGE_FULL}:${VERSION} 2>/dev/null || true
    podman manifest rm ${IMAGE_FULL}:latest 2>/dev/null || true

    # Build for amd64
    echo -e "${GREEN}  ➤${NC} Building linux/amd64..."
    podman build --platform linux/amd64 \
      -t ${IMAGE_FULL}:${VERSION}-amd64 \
      .

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Build failed for amd64${NC}"
        exit 1
    fi

    # Build for arm64
    echo -e "${GREEN}  ➤${NC} Building linux/arm64..."
    podman build --platform linux/arm64 \
      -t ${IMAGE_FULL}:${VERSION}-arm64 \
      .

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Build failed for arm64${NC}"
        exit 1
    fi

    # Create manifest for version tag
    echo -e "${GREEN}  ➤${NC} Creating manifest for ${VERSION}..."
    podman manifest create ${IMAGE_FULL}:${VERSION}
    podman manifest add ${IMAGE_FULL}:${VERSION} ${IMAGE_FULL}:${VERSION}-amd64
    podman manifest add ${IMAGE_FULL}:${VERSION} ${IMAGE_FULL}:${VERSION}-arm64

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Manifest creation failed${NC}"
        exit 1
    fi

    # Create manifest for latest tag
    echo -e "${GREEN}  ➤${NC} Creating manifest for latest..."
    podman manifest create ${IMAGE_FULL}:latest
    podman manifest add ${IMAGE_FULL}:latest ${IMAGE_FULL}:${VERSION}-amd64
    podman manifest add ${IMAGE_FULL}:latest ${IMAGE_FULL}:${VERSION}-arm64

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Manifest creation failed${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓${NC} Build successful"
echo ""

# List the image
echo -e "${GREEN}➤${NC} Image details:"
$CONTAINER_TOOL images ${IMAGE_FULL}
echo ""

# Test the image (use native architecture)
echo -e "${GREEN}➤${NC} Testing image..."
if $CONTAINER_TOOL run --rm ${IMAGE_FULL}:${VERSION} python -c "import sys; sys.exit(0)"; then
    echo -e "${GREEN}✓${NC} Image test passed"
else
    echo -e "${RED}✗ Image test failed${NC}"
    exit 1
fi
echo ""

# Security scan (if trivy is available)
if command -v trivy &> /dev/null; then
    echo -e "${GREEN}➤${NC} Running security scan..."
    trivy image --severity HIGH,CRITICAL ${IMAGE_FULL}:${VERSION}
    echo ""
fi

# Push confirmation
echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}Push to Registry${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo "About to push:"
echo "  • ${IMAGE_FULL}:${VERSION}"
echo "  • ${IMAGE_FULL}:latest"
echo ""
read -p "Continue with push? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Push cancelled"
    exit 0
fi

# Push multi-architecture images
echo ""
if [ "$CONTAINER_TOOL" = "docker" ]; then
    # Docker buildx can push directly during build or separately
    echo -e "${GREEN}➤${NC} Pushing multi-arch images with Docker buildx..."
    docker buildx build \
      --platform ${PLATFORMS} \
      -t ${IMAGE_FULL}:${VERSION} \
      -t ${IMAGE_FULL}:latest \
      --push \
      .

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Push failed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓${NC} Pushed version ${VERSION} and latest (multi-arch)"
else
    # Podman manifest push
    echo -e "${GREEN}➤${NC} Pushing ${IMAGE_FULL}:${VERSION} manifest..."
    podman manifest push ${IMAGE_FULL}:${VERSION} docker://${IMAGE_FULL}:${VERSION}

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Push failed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓${NC} Pushed version ${VERSION}"

    # Push latest manifest
    echo -e "${GREEN}➤${NC} Pushing ${IMAGE_FULL}:latest manifest..."
    podman manifest push ${IMAGE_FULL}:latest docker://${IMAGE_FULL}:latest

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Push failed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓${NC} Pushed latest tag"
fi
echo ""

# Git tag
echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}Git Release${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check if git repo
if [ ! -d .git ]; then
    echo -e "${YELLOW}⚠${NC} Not a git repository, skipping git tag"
else
    # Check if tag already exists
    if git rev-parse "v${VERSION}" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} Git tag v${VERSION} already exists"
    else
        read -p "Create and push git tag v${VERSION}? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git tag -a "v${VERSION}" -m "Release version ${VERSION}"
            git push origin "v${VERSION}"
            echo -e "${GREEN}✓${NC} Git tag v${VERSION} created and pushed"
        fi
    fi
fi

echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}Success!${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo "Multi-architecture container images published:"
echo "  📦 ${IMAGE_FULL}:${VERSION} (linux/amd64, linux/arm64)"
echo "  📦 ${IMAGE_FULL}:latest (linux/amd64, linux/arm64)"
echo ""
echo "To use this image:"
echo ""
echo "  # Pull the image (automatically uses your platform)"
echo "  ${CONTAINER_TOOL} pull ${IMAGE_FULL}:${VERSION}"
echo ""
echo "  # Run with environment variables"
echo "  ${CONTAINER_TOOL} run --rm --env-file .env ${IMAGE_FULL}:${VERSION}"
echo ""
echo "  # Use in Kubernetes"
echo "  Update image: to ${IMAGE_FULL}:${VERSION}"
echo ""
echo "View on GitHub:"
echo "  https://github.com/${GITHUB_USERNAME}?tab=packages"
echo ""
