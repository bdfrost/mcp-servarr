# Contributing to mcp-servarr MCP

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Maintain professionalism in all interactions

## Getting Started

### Prerequisites

- Python 3.12+
- Docker
- Git
- A Sonarr and/or Radarr instance for testing

### Development Setup

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/your-username/mcp_servarr.git
cd mcp_servarr
```

3. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
pip install pytest flake8 black bandit safety
```

5. Copy and configure environment:
```bash
cp .env.example .env
# Edit .env with your Sonarr/Radarr details
```

## Development Workflow

### Creating a Branch

Create a branch for your work:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or changes

### Making Changes

1. Make your changes
2. Follow the code style guidelines (see below)
3. Add tests for new functionality
4. Update documentation as needed

### Testing

Run tests before submitting:
```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_server.py -v

# Run with coverage
pytest --cov=src tests/
```

### Code Quality

Before committing, ensure your code passes all checks:

```bash
# Format code
make format

# Run linter
make lint

# Security checks
bandit -r src/
safety check
```

### Committing

Write clear, descriptive commit messages:
```
feat: add support for Sonarr v4 API
fix: handle timeout errors gracefully
docs: update installation instructions
test: add tests for calendar endpoints
```

Use conventional commits format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting
- `refactor:` - Code restructuring
- `test:` - Testing
- `chore:` - Maintenance

## Pull Request Process

1. Update your branch with the latest main:
```bash
git fetch upstream
git rebase upstream/main
```

2. Push your changes:
```bash
git push origin feature/your-feature-name
```

3. Create a Pull Request on GitHub

4. Fill out the PR template completely:
   - Description of changes
   - Related issues
   - Testing performed
   - Screenshots (if applicable)

5. Wait for review and address feedback

### PR Requirements

- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Commit messages are clear
- [ ] PR description is complete

## Code Style Guidelines

### Python Style

Follow PEP 8 with these specifics:
- Line length: 120 characters
- Use type hints where appropriate
- Use docstrings for functions and classes
- Use meaningful variable names

Example:
```python
async def get_recent_series(self, days: int = 7) -> str:
    """
    Get recently added series from Sonarr.
    
    Args:
        days: Number of days to look back (default: 7)
    
    Returns:
        Formatted string with series information
    """
    # Implementation
```

### Formatting

Use Black for formatting:
```bash
black src/
```

### Imports

Order imports:
1. Standard library
2. Third-party packages
3. Local modules

```python
import os
from typing import Optional

import httpx
from pydantic import BaseModel

from src.utils import format_date
```

## Adding New Features

### New API Endpoints

When adding new Sonarr/Radarr endpoints:

1. Add method to the appropriate class
2. Add tool definition in `list_tools()`
3. Add handler in `call_tool()`
4. Add tests
5. Update README with new tool

Example:
```python
async def get_tags(self) -> str:
    """Get all tags from Sonarr"""
    tags = await self.sonarr_client.get("tag")
    # Format and return
```

### New Tools

Follow this structure:
```python
Tool(
    name="service_action_resource",
    description="Clear description of what the tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param"]
    }
)
```

## Testing Guidelines

### Test Structure

- One test file per source file
- Group tests by class/functionality
- Use descriptive test names
- Mock external dependencies

Example:
```python
class TestSonarrFeatures:
    """Test Sonarr-specific features"""
    
    @pytest.mark.asyncio
    async def test_get_recent_series_empty(self):
        """Test getting recent series when none exist"""
        # Test implementation
```

### Test Coverage

Aim for >80% code coverage:
```bash
pytest --cov=src --cov-report=html tests/
```

## Documentation

### Code Documentation

- Add docstrings to all functions and classes
- Use type hints
- Include examples in docstrings when helpful
- Document exceptions that may be raised

### User Documentation

Update README.md for:
- New features
- Changed behavior
- New configuration options
- Breaking changes

### API Documentation

Document new tools:
- Tool name and purpose
- Parameters and types
- Return format
- Usage examples

## Security

### Reporting Vulnerabilities

See SECURITY.md for reporting process.

### Security Guidelines

- Never commit API keys or secrets
- Validate all inputs
- Use parameterized queries
- Follow principle of least privilege
- Keep dependencies updated

## Release Process

Releases are handled by maintainers:

1. Update version numbers
2. Update CHANGELOG.md
3. Tag release
4. Build and push container images
5. Update documentation

## Getting Help

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues before creating new ones
- Provide clear reproduction steps for bugs

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

## Questions?

Don't hesitate to ask! We're here to help:
- Open a discussion on GitHub
- Comment on related issues
- Reach out to maintainers

Thank you for contributing! 🎉
