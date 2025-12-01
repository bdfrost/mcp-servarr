#!/bin/bash

# Sonarr-Radarr MCP - Build and Push Script for Podman
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
IMAGE_NAME="sonarr-radarr-mcp"
REGISTRY="ghcr.io"

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

# Check if podman is installed
if ! command -v podman &> /dev/null; then
    echo -e "${RED}Error: podman is not installed${NC}"
    exit 1
fi

# Check if logged in to ghcr.io
if ! podman login ghcr.io --get-login &> /dev/null; then
    echo -e "${YELLOW}Warning: Not logged in to ghcr.io${NC}"
    echo "Please login first:"
    echo "  echo \$GITHUB_TOKEN | podman login ghcr.io -u $GITHUB_USERNAME --password-stdin"
    exit 1
fi

IMAGE_FULL="${REGISTRY}/${GITHUB_USERNAME}/${IMAGE_NAME}"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}Building Container Image${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo "Image: ${IMAGE_FULL}"
echo "Version: ${VERSION}"
echo ""

# Build the image
echo -e "${GREEN}➤${NC} Building ${IMAGE_NAME}:${VERSION}..."
podman build \
  -t ${IMAGE_FULL}:${VERSION} \
  -t ${IMAGE_FULL}:latest \
  .

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Build successful"
echo ""

# List the image
echo -e "${GREEN}➤${NC} Image details:"
podman images ${IMAGE_FULL}
echo ""

# Test the image
echo -e "${GREEN}➤${NC} Testing image..."
if podman run --rm ${IMAGE_FULL}:${VERSION} python -c "import sys; sys.exit(0)"; then
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

# Push version tag
echo ""
echo -e "${GREEN}➤${NC} Pushing ${IMAGE_FULL}:${VERSION}..."
podman push ${IMAGE_FULL}:${VERSION}

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Push failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Pushed version ${VERSION}"

# Push latest tag
echo -e "${GREEN}➤${NC} Pushing ${IMAGE_FULL}:latest..."
podman push ${IMAGE_FULL}:latest

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Push failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Pushed latest tag"
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
echo "Container image published:"
echo "  📦 ${IMAGE_FULL}:${VERSION}"
echo "  📦 ${IMAGE_FULL}:latest"
echo ""
echo "To use this image:"
echo ""
echo "  # Pull the image"
echo "  podman pull ${IMAGE_FULL}:${VERSION}"
echo ""
echo "  # Run with environment variables"
echo "  podman run --rm --env-file .env ${IMAGE_FULL}:${VERSION}"
echo ""
echo "  # Use in Kubernetes"
echo "  Update image: to ${IMAGE_FULL}:${VERSION}"
echo ""
echo "View on GitHub:"
echo "  https://github.com/${GITHUB_USERNAME}?tab=packages"
echo ""
