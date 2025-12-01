# Docker Deployment Modes

This project supports two distinct deployment modes with separate Docker configurations.

## Mode Comparison

| Feature | REST API Mode | MCP stdio Mode |
|---------|---------------|----------------|
| **Dockerfile** | `Dockerfile` | `Dockerfile.local` |
| **Compose File** | `docker-compose.yml` | `docker-compose.local.yml` |
| **Entrypoint** | `src/http_server.py` | `src/server.py` |
| **Protocol** | HTTP REST API | MCP stdio |
| **Port** | 8080 | None |
| **Use Case** | Kubernetes/Production | Local testing with Claude Desktop |
| **Health Check** | HTTP `/health` endpoint | Basic Python validation |
| **Interactive** | No | Yes (stdin/stdout) |

## REST API Mode

### Purpose
Production-ready HTTP server for Kubernetes deployments.

### Build and Run
```bash
# Build
make build
# or
docker build -t mcp-servarr:latest .

# Run
make run
# Access at http://localhost:8080
```

### Endpoints
- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /api/sonarr/*` - Sonarr operations
- `GET /api/radarr/*` - Radarr operations

### Example Request
```bash
curl http://localhost:8080/api/sonarr/status
curl "http://localhost:8080/api/radarr/search?query=Inception"
```

## MCP stdio Mode

### Purpose
Local development and testing with MCP Inspector or Claude Desktop.

### Build and Run
```bash
# Build
make build-local
# or
docker build -f Dockerfile.local -t mcp-servarr:local .

# Run interactively
docker run --rm -it --env-file .env mcp-servarr:local

# Run with docker-compose
make run-local
```

### Testing with MCP Inspector
```bash
# Build the image first
make build-local

# Run MCP Inspector
npx @modelcontextprotocol/inspector docker run --rm -i --env-file .env mcp-servarr:local
```

### Claude Desktop Configuration
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-servarr": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file",
        "/absolute/path/to/.env",
        "mcp-servarr:local"
      ]
    }
  }
}
```

## Quick Commands Reference

```bash
# Build both modes
make build-all

# REST API Mode
make build         # Build image
make run           # Run in foreground
make run-detached  # Run in background
make logs          # View logs
make stop          # Stop service

# MCP stdio Mode
make build-local         # Build image
make run-local           # Run in foreground
make run-local-detached  # Run in background
make logs-local          # View logs
make stop-local          # Stop service

# Cleanup
make clean  # Remove all containers and images
```

## Which Mode Should I Use?

### Use REST API Mode (Dockerfile) when:
- Deploying to Kubernetes
- Need HTTP endpoints for monitoring/health checks
- Running in production
- Integrating with other HTTP services
- Need to access via curl/Postman

### Use MCP stdio Mode (Dockerfile.local) when:
- Testing with Claude Desktop locally
- Developing new MCP tools
- Using MCP Inspector for debugging
- Running integration tests
- Need stdio protocol communication

## Security

Both modes maintain the same security posture:
- Non-root user (UID 1000)
- Read-only filesystem
- Dropped capabilities
- No privilege escalation
- Resource limits enforced

See `SECURITY.md` for complete security details.
