FROM python:3.12-slim

# Security: Create non-root user
RUN groupadd -r mcp && useradd -r -g mcp mcp

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Security: Set ownership and permissions
RUN chown -R mcp:mcp /app && \
    chmod -R 555 /app/src && \
    chmod 555 /app

# Security: Switch to non-root user
USER mcp

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Set Python to run in unbuffered mode for better logging
ENV PYTHONUNBUFFERED=1

# Run the MCP server
ENTRYPOINT ["python", "-u", "src/server.py"]
