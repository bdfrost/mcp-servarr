#!/usr/bin/env python3
"""
HTTP REST API wrapper for Sonarr-Radarr MCP Server
Provides HTTP endpoints for Kubernetes deployment
"""

import os
import logging
from typing import Any, Dict, Optional
from datetime import datetime, timezone, timedelta

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.requests import Request
import uvicorn

from server import SonarrRadarrMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-servarr-http")

# Global MCP instance
mcp_instance: Optional[SonarrRadarrMCP] = None


async def startup():
    """Initialize MCP server on startup"""
    global mcp_instance
    mcp_instance = SonarrRadarrMCP()
    logger.info("MCP server initialized in HTTP mode")


async def shutdown():
    """Cleanup on shutdown"""
    global mcp_instance
    if mcp_instance:
        await mcp_instance.cleanup()
        logger.info("MCP server cleaned up")


async def health(request: Request):
    """Health check endpoint for Kubernetes"""
    return JSONResponse({"status": "healthy"})


async def readiness(request: Request):
    """Readiness check endpoint for Kubernetes"""
    if mcp_instance is None:
        return JSONResponse({"status": "not ready"}, status_code=503)

    return JSONResponse({
        "status": "ready",
        "sonarr_configured": mcp_instance.sonarr_client is not None,
        "radarr_configured": mcp_instance.radarr_client is not None
    })


# Sonarr endpoints
async def sonarr_recent_series(request: Request):
    """Get recently added series"""
    if not mcp_instance or not mcp_instance.sonarr_client:
        return JSONResponse({"error": "Sonarr not configured"}, status_code=503)

    days = int(request.query_params.get("days", 7))
    try:
        result = await mcp_instance.get_recent_series(days)
        return JSONResponse({"result": result})
    except Exception as e:
        logger.error(f"Error getting recent series: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


async def sonarr_calendar(request: Request):
    """Get Sonarr calendar"""
    if not mcp_instance or not mcp_instance.sonarr_client:
        return JSONResponse({"error": "Sonarr not configured"}, status_code=503)

    days = int(request.query_params.get("days", 7))
    try:
        result = await mcp_instance.get_sonarr_calendar(days)
        return JSONResponse({"result": result})
    except Exception as e:
        logger.error(f"Error getting calendar: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


async def sonarr_search(request: Request):
    """Search for series"""
    if not mcp_instance or not mcp_instance.sonarr_client:
        return JSONResponse({"error": "Sonarr not configured"}, status_code=503)

    query = request.query_params.get("query", "")
    if not query:
        return JSONResponse({"error": "query parameter required"}, status_code=400)

    try:
        result = await mcp_instance.search_sonarr_series(query)
        return JSONResponse({"result": result})
    except Exception as e:
        logger.error(f"Error searching series: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


async def sonarr_status(request: Request):
    """Get Sonarr system status"""
    if not mcp_instance or not mcp_instance.sonarr_client:
        return JSONResponse({"error": "Sonarr not configured"}, status_code=503)

    try:
        result = await mcp_instance.get_sonarr_status()
        return JSONResponse({"result": result})
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


async def sonarr_queue(request: Request):
    """Get Sonarr download queue"""
    if not mcp_instance or not mcp_instance.sonarr_client:
        return JSONResponse({"error": "Sonarr not configured"}, status_code=503)

    try:
        result = await mcp_instance.get_sonarr_queue()
        return JSONResponse({"result": result})
    except Exception as e:
        logger.error(f"Error getting queue: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


# Radarr endpoints
async def radarr_recent_movies(request: Request):
    """Get recently added movies"""
    if not mcp_instance or not mcp_instance.radarr_client:
        return JSONResponse({"error": "Radarr not configured"}, status_code=503)

    days = int(request.query_params.get("days", 7))
    try:
        result = await mcp_instance.get_recent_movies(days)
        return JSONResponse({"result": result})
    except Exception as e:
        logger.error(f"Error getting recent movies: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


async def radarr_calendar(request: Request):
    """Get Radarr calendar"""
    if not mcp_instance or not mcp_instance.radarr_client:
        return JSONResponse({"error": "Radarr not configured"}, status_code=503)

    days = int(request.query_params.get("days", 30))
    try:
        result = await mcp_instance.get_radarr_calendar(days)
        return JSONResponse({"result": result})
    except Exception as e:
        logger.error(f"Error getting calendar: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


async def radarr_search(request: Request):
    """Search for movies"""
    if not mcp_instance or not mcp_instance.radarr_client:
        return JSONResponse({"error": "Radarr not configured"}, status_code=503)

    query = request.query_params.get("query", "")
    if not query:
        return JSONResponse({"error": "query parameter required"}, status_code=400)

    try:
        result = await mcp_instance.search_radarr_movies(query)
        return JSONResponse({"result": result})
    except Exception as e:
        logger.error(f"Error searching movies: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


async def radarr_status(request: Request):
    """Get Radarr system status"""
    if not mcp_instance or not mcp_instance.radarr_client:
        return JSONResponse({"error": "Radarr not configured"}, status_code=503)

    try:
        result = await mcp_instance.get_radarr_status()
        return JSONResponse({"result": result})
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


async def radarr_queue(request: Request):
    """Get Radarr download queue"""
    if not mcp_instance or not mcp_instance.radarr_client:
        return JSONResponse({"error": "Radarr not configured"}, status_code=503)

    try:
        result = await mcp_instance.get_radarr_queue()
        return JSONResponse({"result": result})
    except Exception as e:
        logger.error(f"Error getting queue: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


# Create Starlette app
app = Starlette(
    debug=False,
    routes=[
        # Health checks
        Route("/health", health),
        Route("/ready", readiness),

        # Sonarr endpoints
        Route("/api/sonarr/recent", sonarr_recent_series),
        Route("/api/sonarr/calendar", sonarr_calendar),
        Route("/api/sonarr/search", sonarr_search),
        Route("/api/sonarr/status", sonarr_status),
        Route("/api/sonarr/queue", sonarr_queue),

        # Radarr endpoints
        Route("/api/radarr/recent", radarr_recent_movies),
        Route("/api/radarr/calendar", radarr_calendar),
        Route("/api/radarr/search", radarr_search),
        Route("/api/radarr/status", radarr_status),
        Route("/api/radarr/queue", radarr_queue),
    ],
    on_startup=[startup],
    on_shutdown=[shutdown],
)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
