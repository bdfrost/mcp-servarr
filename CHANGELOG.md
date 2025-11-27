# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-26

### Added
- Initial release of mcp-servarr MCP Server
- Sonarr integration with 7 tools:
  - Get recent series
  - View calendar/upcoming episodes
  - Search series
  - System status
  - Download queue
  - Refresh series
  - Search episodes
- Radarr integration with 7 tools:
  - Get recent movies
  - View calendar/upcoming releases
  - Search movies
  - System status
  - Download queue
  - Refresh movie
  - Search movie
- Docker container with security hardening
- Kubernetes deployment manifests
- Docker Compose configuration
- Comprehensive documentation (README, SECURITY, CONTRIBUTING)
- GitHub Actions CI/CD pipeline
- Security scanning (Trivy, Bandit)
- Unit tests with pytest
- Setup automation script

### Security
- Non-root container execution (UID 1000)
- Read-only root filesystem
- Dropped all Linux capabilities
- Pod Security Standards compliance
- Network policies for ingress/egress
- Secrets management for API keys
- Resource limits and quotas
- Seccomp profile configuration

### Documentation
- Complete README with setup instructions
- Security policy and best practices
- Contributing guidelines
- License (MIT)
- Example configurations
- Troubleshooting guide

## [Unreleased]

### Planned
- Additional Sonarr/Radarr endpoints
- Webhook support for real-time updates
- Enhanced error handling
- Performance optimizations
- Integration tests
- Metrics and monitoring endpoints
