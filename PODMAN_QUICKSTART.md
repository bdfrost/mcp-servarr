# Podman Quick Reference for GitHub Container Registry

## One-Time Setup

### 1. Create GitHub Personal Access Token
```
GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
→ Generate new token → Select: write:packages
```

### 2. Login to GitHub Container Registry
```bash
export GITHUB_TOKEN=ghp_your_token_here
echo $GITHUB_TOKEN | podman login ghcr.io -u YOUR_USERNAME --password-stdin
```

## Building and Pushing (Easy Way)

### Use the automated script:
```bash
# Make sure you're in the project directory
cd sonarr-radarr-mcp

# Build and push version 0.1
./build-and-push.sh 0.1 YOUR_USERNAME

# Build and push version 0.2
./build-and-push.sh 0.2 YOUR_USERNAME
```

## Manual Commands

### Build
```bash
podman build -t ghcr.io/YOUR_USERNAME/sonarr-radarr-mcp:0.1 .
podman tag ghcr.io/YOUR_USERNAME/sonarr-radarr-mcp:0.1 \
            ghcr.io/YOUR_USERNAME/sonarr-radarr-mcp:latest
```

### Test
```bash
podman run --rm --env-file .env ghcr.io/YOUR_USERNAME/sonarr-radarr-mcp:0.1
```

### Push
```bash
podman push ghcr.io/YOUR_USERNAME/sonarr-radarr-mcp:0.1
podman push ghcr.io/YOUR_USERNAME/sonarr-radarr-mcp:latest
```

### Git Tag
```bash
git tag -a v0.1 -m "Release version 0.1"
git push origin v0.1
```

## Using Your Published Image

### Pull
```bash
podman pull ghcr.io/YOUR_USERNAME/sonarr-radarr-mcp:0.1
```

### Run
```bash
podman run --rm \
  -e SONARR_URL=http://sonarr:8989 \
  -e SONARR_API_KEY=your-key \
  -e RADARR_URL=http://radarr:7878 \
  -e RADARR_API_KEY=your-key \
  ghcr.io/YOUR_USERNAME/sonarr-radarr-mcp:0.1
```

## Troubleshooting

### Check if logged in
```bash
podman login ghcr.io --get-login
```

### Re-login
```bash
podman logout ghcr.io
echo $GITHUB_TOKEN | podman login ghcr.io -u YOUR_USERNAME --password-stdin
```

### List local images
```bash
podman images ghcr.io/YOUR_USERNAME/sonarr-radarr-mcp
```

### Remove local image
```bash
podman rmi ghcr.io/YOUR_USERNAME/sonarr-radarr-mcp:0.1
```

## Making Package Public

1. Go to: https://github.com/YOUR_USERNAME?tab=packages
2. Click on sonarr-radarr-mcp
3. Package settings → Change visibility → Public

## Your Image URL

After pushing, your image will be available at:
```
ghcr.io/YOUR_USERNAME/sonarr-radarr-mcp:0.1
```

Share this URL in your README for others to use!
