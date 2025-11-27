# Security Policy

## Overview

This MCP server is designed with security as a top priority. This document outlines the security measures implemented and best practices for deployment.

## Security Features

### Container Security

1. **Non-Root User Execution**
   - Container runs as UID 1000 (non-root)
   - User and group `mcp` created specifically for the application
   - Prevents privilege escalation attacks

2. **Read-Only Root Filesystem**
   - Root filesystem is mounted as read-only
   - Only `/tmp` and `/home/mcp` are writable (via tmpfs)
   - Prevents unauthorized file modifications

3. **Dropped Capabilities**
   - All Linux capabilities are dropped
   - `allowPrivilegeEscalation: false` prevents gaining additional privileges
   - Minimal attack surface

4. **Seccomp Profile**
   - Uses the RuntimeDefault seccomp profile
   - Restricts system calls available to the container

### Kubernetes Security

1. **Pod Security Standards**
   - Implements restricted Pod Security Standards
   - Non-root execution enforced
   - No host namespace access

2. **Network Policies**
   - Restricts ingress to only necessary services
   - Limits egress to DNS, Sonarr, and Radarr
   - Default deny policy

3. **Secrets Management**
   - API keys stored in Kubernetes Secrets
   - Secrets mounted as environment variables
   - Never stored in container images or ConfigMaps

4. **Resource Limits**
   - CPU and memory limits prevent resource exhaustion
   - Protects cluster from DoS scenarios

### Application Security

1. **API Key Protection**
   - API keys never logged
   - Transmitted only in HTTP headers
   - Not exposed in error messages

2. **Input Validation**
   - All user inputs validated
   - Type checking via Pydantic models
   - Prevents injection attacks

3. **Error Handling**
   - Sensitive information not exposed in errors
   - Proper exception handling throughout
   - Graceful degradation

4. **HTTP Security**
   - Request timeouts configured
   - Connection pooling managed
   - No credential exposure in URLs

## Deployment Best Practices

### API Key Management

**DO:**
- Use Kubernetes Secrets for production
- Rotate API keys regularly (every 90 days recommended)
- Use separate API keys per environment
- Limit API key permissions in Sonarr/Radarr
- Enable audit logging for API key usage

**DON'T:**
- Store API keys in version control
- Share API keys between environments
- Use the same key for multiple services
- Log API keys
- Include API keys in container images

### Network Security

**DO:**
- Use TLS/HTTPS for Sonarr/Radarr connections
- Implement network policies
- Restrict ingress to trusted sources only
- Use private networks when possible
- Enable mutual TLS if available

**DON'T:**
- Expose services directly to the internet
- Allow unrestricted egress
- Use plain HTTP for sensitive data
- Disable SSL verification

### Container Security

**DO:**
- Scan images for vulnerabilities regularly
- Use minimal base images
- Keep dependencies updated
- Use specific version tags (avoid `latest`)
- Sign container images

**DON'T:**
- Run containers as root
- Use privileged containers
- Mount host filesystem
- Disable security features
- Use outdated base images

### Kubernetes Security

**DO:**
- Enable Pod Security Admission
- Use RBAC with least privilege
- Implement network policies
- Enable audit logging
- Use namespaces for isolation

**DON'T:**
- Grant cluster-admin unnecessarily
- Use default service accounts
- Expose sensitive ports
- Disable security policies
- Mix environments in same namespace

## Vulnerability Reporting

If you discover a security vulnerability, please:

1. **DO NOT** open a public issue
2. Email security details to: [your-security-email]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to address the issue.

## Security Updates

### Checking for Updates

Monitor these sources for security updates:
- Python dependencies: `pip list --outdated`
- Base image: Check Python Docker Hub releases
- MCP SDK: Check Anthropic's repository

### Update Process

1. Review release notes for security fixes
2. Test updates in non-production environment
3. Update `requirements.txt` with specific versions
4. Rebuild container image
5. Scan for vulnerabilities
6. Deploy to production

### Update Schedule

- **Critical vulnerabilities**: Immediate update
- **High severity**: Within 7 days
- **Medium severity**: Within 30 days
- **Low severity**: Next regular update cycle

## Security Checklist

### Pre-Deployment

- [ ] API keys generated and stored securely
- [ ] Network policies reviewed and tested
- [ ] Resource limits configured
- [ ] Security contexts verified
- [ ] Image scanned for vulnerabilities
- [ ] Secrets properly configured
- [ ] TLS/HTTPS enabled for services
- [ ] Documentation reviewed

### Post-Deployment

- [ ] Verify non-root execution
- [ ] Check network policies are enforced
- [ ] Confirm secrets are not exposed
- [ ] Test API connectivity
- [ ] Review logs for errors
- [ ] Verify resource limits
- [ ] Test failover scenarios

### Ongoing

- [ ] Monitor security advisories
- [ ] Rotate API keys quarterly
- [ ] Update dependencies monthly
- [ ] Review access logs weekly
- [ ] Scan for vulnerabilities monthly
- [ ] Conduct security audits annually

## Compliance

### Data Handling

This MCP server:
- Does NOT store media files
- Does NOT log sensitive information
- Does NOT retain API responses
- Operates in-memory only
- Has no persistent storage

### Audit Logging

For compliance requirements:
1. Enable Kubernetes audit logging
2. Monitor API access patterns
3. Log authentication attempts
4. Track configuration changes
5. Implement log retention policies

## Known Limitations

1. **API Key Security**: Keys stored in environment variables (use secrets manager for enhanced security)
2. **Network Access**: Requires network access to Sonarr/Radarr (use mTLS for enhanced security)
3. **Read-Only Operations**: Most operations are read-only, but some modify metadata

## Security Hardening

### Additional Steps (Optional)

1. **AppArmor/SELinux**
   - Configure mandatory access control
   - Create custom profiles

2. **Image Signing**
   - Sign images with Cosign
   - Implement admission controller

3. **Runtime Security**
   - Deploy Falco for runtime monitoring
   - Configure security alerts

4. **Secrets Management**
   - Use HashiCorp Vault
   - Implement External Secrets Operator

5. **Network Security**
   - Implement service mesh (Istio, Linkerd)
   - Enable mutual TLS
   - Use network segmentation

## References

- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security.html)

## Contact

For security questions or concerns:
- Email: [your-security-email]
- Security advisories: [GitHub Security Advisories URL]

---

Last Updated: 2025-11-26
