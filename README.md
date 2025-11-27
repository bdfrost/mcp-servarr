# Sonarr & Radarr MCP Server

A secure, production-ready Model Context Protocol (MCP) server for interacting with Sonarr and Radarr APIs. This server enables Claude to query your media library, check recent additions, view upcoming releases, and perform basic management tasks.

## Features

### Sonarr
- Get recently added TV series
- View upcoming episode calendar
- Search series in your library
- Check system status and disk space
- View download queue
- Refresh series metadata
- Trigger episode searches

### Radarr
- Get recently added movies
- View upcoming movie releases
- Search movies in your library
- Check system status and disk space
- View download queue
- Refresh movie metadata
- Trigger movie searches

## Security Features

This MCP server is built with security as a priority:

- **Non-root container execution**: Runs as user ID 1000 (non-root)
- **Read-only root filesystem**: Container filesystem is immutable
- **No privilege escalation**: Container cannot gain additional privileges
- **Dropped capabilities**: All Linux capabilities dropped
- **Secrets management**: API keys stored in Kubernetes secrets
- **Network policies**: Restricts network access to only necessary services
- **Resource limits**: CPU and memory limits prevent resource exhaustion
- **Secure defaults**: Follows security best practices from the ground up

## Prerequisites

- Docker (for containerization)
- Kubernetes cluster (for deployment)
- Sonarr instance with API access
- Radarr instance with API access
- Python 3.12+ (for local development)

## Quick Start

### 1. Clone and Configure

```bash
git clone <your-repo-url>
cd mcp_servarr
```

### 2. Set Up Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```bash
# Sonarr Configuration
SONARR_URL=http://your-sonarr-host:8989
SONARR_API_KEY=your-sonarr-api-key

# Radarr Configuration
RADARR_URL=http://your-radarr-host:7878
RADARR_API_KEY=your-radarr-api-key
```

**Finding your API keys:**
- Sonarr: Settings → General → Security → API Key
- Radarr: Settings → General → Security → API Key

### 3. Build the Docker Image

```bash
docker build -t mcp_servarr:latest .
```

### 4. Test Locally with Docker Compose

```bash
docker-compose up
```

## Kubernetes Deployment

### 1. Update Secrets

Edit `k8s/deployment.yaml` and replace the placeholder API keys in the Secret:

```yaml
stringData:
  SONARR_URL: "http://sonarr.media.svc.cluster.local:8989"
  SONARR_API_KEY: "your-actual-sonarr-api-key"
  RADARR_URL: "http://radarr.media.svc.cluster.local:7878"
  RADARR_API_KEY: "your-actual-radarr-api-key"
```

**Security Note:** For production, use `kubectl create secret` instead of storing secrets in YAML:

```bash
kubectl create secret generic mcp_servarr-secrets \
  --namespace=mcp-servarr \
  --from-literal=SONARR_URL='http://sonarr:8989' \
  --from-literal=SONARR_API_KEY='your-key' \
  --from-literal=RADARR_URL='http://radarr:7878' \
  --from-literal=RADARR_API_KEY='your-key'
```

### 2. Deploy to Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
```

### 3. Verify Deployment

```bash
kubectl get pods -n mcp-servarr
kubectl logs -n mcp-servarr deployment/mcp_servarr
```

## Connecting to Claude

To use this MCP server with Claude Desktop, add it to your MCP settings:

### Using Docker

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "mcp-servarr": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file", "/path/to/your/.env",
        "mcp_servarr:latest"
      ]
    }
  }
}
```

### Using Python (Development)

```json
{
  "mcpServers": {
    "mcp-servarr": {
      "command": "python",
      "args": [
        "/path/to/mcp_servarr/src/server.py"
      ],
      "env": {
        "SONARR_URL": "http://localhost:8989",
        "SONARR_API_KEY": "your-key",
        "RADARR_URL": "http://localhost:7878",
        "RADARR_API_KEY": "your-key"
      }
    }
  }
}
```

## Usage Examples

Once connected to Claude, you can ask questions like:

- "What TV shows were added to Sonarr this week?"
- "What movies are coming out in the next 30 days?"
- "Search for Breaking Bad in my library"
- "What's currently downloading in Radarr?"
- "Show me Sonarr's system status"
- "Refresh the metadata for series ID 123"

## API Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SONARR_URL` | No* | - | Sonarr base URL (e.g., http://sonarr:8989) |
| `SONARR_API_KEY` | No* | - | Sonarr API key |
| `RADARR_URL` | No* | - | Radarr base URL (e.g., http://radarr:7878) |
| `RADARR_API_KEY` | No* | - | Radarr API key |
| `REQUEST_TIMEOUT` | No | 30 | HTTP request timeout in seconds |

*At least one service (Sonarr or Radarr) must be configured

### Available Tools

#### Sonarr Tools
- `sonarr_get_recent_series` - Get recently added series
- `sonarr_get_calendar` - Get upcoming episodes
- `sonarr_search_series` - Search for series
- `sonarr_get_system_status` - Get system status
- `sonarr_get_queue` - Get download queue
- `sonarr_refresh_series` - Refresh series metadata
- `sonarr_search_episodes` - Search for missing episodes

#### Radarr Tools
- `radarr_get_recent_movies` - Get recently added movies
- `radarr_get_calendar` - Get upcoming releases
- `radarr_search_movies` - Search for movies
- `radarr_get_system_status` - Get system status
- `radarr_get_queue` - Get download queue
- `radarr_refresh_movie` - Refresh movie metadata
- `radarr_search_movie` - Search for a movie

## Development

### Local Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
export SONARR_URL=http://localhost:8989
export SONARR_API_KEY=your-key
export RADARR_URL=http://localhost:7878
export RADARR_API_KEY=your-key
python src/server.py
```

### Testing

Test the server using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python src/server.py
```

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to Sonarr/Radarr

**Solutions**:
- Verify URLs are correct (include http:// or https://)
- Check API keys are valid
- Ensure Sonarr/Radarr are accessible from the container
- Check network policies in Kubernetes

### Permission Errors

**Problem**: Container fails with permission errors

**Solutions**:
- Verify the container runs as non-root (UID 1000)
- Check volume mount permissions
- Ensure read-only filesystem is properly configured

### API Rate Limiting

**Problem**: Getting rate limited by APIs

**Solutions**:
- Increase `REQUEST_TIMEOUT` if requests are timing out
- Reduce frequency of queries
- Check Sonarr/Radarr logs for issues

## Security Considerations

### Production Deployment Checklist

- [ ] Use Kubernetes Secrets for API keys (not ConfigMaps)
- [ ] Enable Pod Security Standards (restricted profile)
- [ ] Configure network policies to limit egress traffic
- [ ] Set appropriate resource limits
- [ ] Enable audit logging
- [ ] Use private container registry
- [ ] Scan images for vulnerabilities
- [ ] Rotate API keys regularly
- [ ] Use TLS for Sonarr/Radarr connections
- [ ] Implement monitoring and alerting

### API Key Security

**Never commit API keys to version control!**

For production:
1. Use Kubernetes secrets
2. Consider using a secrets manager (Vault, Sealed Secrets, etc.)
3. Rotate keys regularly
4. Use separate API keys for different environments
5. Enable API key authentication logging in Sonarr/Radarr

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Guidelines
- Follow existing code style
- Add tests for new features
- Update documentation
- Ensure security best practices
- Test in both Docker and Kubernetes

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

- Built with the [Model Context Protocol SDK](https://github.com/anthropics/anthropic-mcp-sdk)
- Uses [Sonarr API](https://sonarr.tv/)
- Uses [Radarr API](https://radarr.video/)
