#!/bin/bash

# mcp-servarr MCP Setup Script
# This script helps you set up the MCP server quickly

set -e

echo "=================================="
echo "mcp-servarr MCP Setup"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}✗${NC} $1 is not installed"
        return 1
    else
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    fi
}

MISSING_DEPS=0

check_command python3 || MISSING_DEPS=1
check_command docker || MISSING_DEPS=1
check_command kubectl || echo -e "${YELLOW}⚠${NC} kubectl not found (optional for Kubernetes deployment)"

if [ $MISSING_DEPS -eq 1 ]; then
    echo -e "\n${RED}Missing required dependencies. Please install them first.${NC}"
    exit 1
fi

echo ""
echo "=================================="
echo "Configuration"
echo "=================================="
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo -e "${YELLOW}⚠${NC} .env file already exists."
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file."
        USE_EXISTING=1
    else
        USE_EXISTING=0
    fi
else
    USE_EXISTING=0
fi

if [ $USE_EXISTING -eq 0 ]; then
    # Get Sonarr configuration
    echo "Sonarr Configuration:"
    read -p "Sonarr URL (e.g., http://sonarr:8989): " SONARR_URL
    read -p "Sonarr API Key: " SONARR_API_KEY
    echo ""

    # Get Radarr configuration
    echo "Radarr Configuration:"
    read -p "Radarr URL (e.g., http://radarr:7878): " RADARR_URL
    read -p "Radarr API Key: " RADARR_API_KEY
    echo ""

    # Create .env file
    cat > .env << EOF
# Sonarr Configuration
SONARR_URL=${SONARR_URL}
SONARR_API_KEY=${SONARR_API_KEY}

# Radarr Configuration
RADARR_URL=${RADARR_URL}
RADARR_API_KEY=${RADARR_API_KEY}

# Optional: Request timeout in seconds
REQUEST_TIMEOUT=30
EOF

    echo -e "${GREEN}✓${NC} .env file created"
fi

echo ""
echo "=================================="
echo "Deployment Method"
echo "=================================="
echo ""
echo "Choose deployment method:"
echo "1) Docker Compose (local)"
echo "2) Kubernetes"
echo "3) Python Development Mode"
echo "4) Skip deployment"
echo ""
read -p "Enter choice (1-4): " -n 1 -r DEPLOY_METHOD
echo ""
echo ""

case $DEPLOY_METHOD in
    1)
        echo "Building and starting with Docker Compose..."
        docker build -t mcp-servarr:latest .
        docker-compose up -d
        echo ""
        echo -e "${GREEN}✓${NC} MCP server started with Docker Compose"
        echo "View logs: docker-compose logs -f"
        ;;
    2)
        echo "Preparing Kubernetes deployment..."
        
        # Check if kubectl is available
        if ! command -v kubectl &> /dev/null; then
            echo -e "${RED}✗${NC} kubectl is required for Kubernetes deployment"
            exit 1
        fi
        
        # Build image
        echo "Building Docker image..."
        docker build -t mcp-servarr:latest .
        
        # Create namespace
        kubectl create namespace mcp-servarr --dry-run=client -o yaml | kubectl apply -f -
        
        # Create secret
        echo "Creating Kubernetes secret..."
        kubectl create secret generic mcp-servarr-secrets \
            --namespace=mcp-servarr \
            --from-literal=SONARR_URL="${SONARR_URL}" \
            --from-literal=SONARR_API_KEY="${SONARR_API_KEY}" \
            --from-literal=RADARR_URL="${RADARR_URL}" \
            --from-literal=RADARR_API_KEY="${RADARR_API_KEY}" \
            --dry-run=client -o yaml | kubectl apply -f -
        
        # Deploy
        echo "Deploying to Kubernetes..."
        kubectl apply -f k8s/deployment.yaml
        
        echo ""
        echo -e "${GREEN}✓${NC} Deployed to Kubernetes"
        echo "Check status: kubectl get pods -n mcp-servarr"
        echo "View logs: kubectl logs -n mcp-servarr -l app=mcp-servarr -f"
        ;;
    3)
        echo "Setting up Python development environment..."
        
        # Create virtual environment if it doesn't exist
        if [ ! -d "venv" ]; then
            python3 -m venv venv
            echo -e "${GREEN}✓${NC} Virtual environment created"
        fi
        
        # Activate and install
        source venv/bin/activate
        pip install -r requirements.txt
        
        echo ""
        echo -e "${GREEN}✓${NC} Development environment ready"
        echo "Run the server: source venv/bin/activate && python src/server.py"
        ;;
    4)
        echo "Skipping deployment."
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "=================================="
echo "Next Steps"
echo "=================================="
echo ""
echo "1. Configure Claude Desktop to use this MCP server"
echo "   Location: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "2. Add this configuration:"
echo '   {
     "mcpServers": {
       "mcp-servarr": {
         "command": "docker",
         "args": [
           "run", "--rm", "-i",
           "--env-file", "'$(pwd)'/.env",
           "mcp-servarr:latest"
         ]
       }
     }
   }'
echo ""
echo "3. Restart Claude Desktop"
echo ""
echo "4. Try asking Claude:"
echo "   - What TV shows were added this week?"
echo "   - What movies are coming out soon?"
echo "   - Show me Sonarr's system status"
echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
