#!/usr/bin/env python3
"""
Sonarr and Radarr MCP Server
A Model Context Protocol server for interacting with Sonarr and Radarr APIs
"""

import os
import asyncio
import logging
from typing import Any, Optional
from datetime import datetime, timedelta

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_servarr")


class Config(BaseModel):
    """Configuration from environment variables"""
    sonarr_url: str = Field(default="")
    sonarr_api_key: str = Field(default="")
    radarr_url: str = Field(default="")
    radarr_api_key: str = Field(default="")
    request_timeout: int = Field(default=30)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        return cls(
            sonarr_url=os.getenv("SONARR_URL", "").rstrip("/"),
            sonarr_api_key=os.getenv("SONARR_API_KEY", ""),
            radarr_url=os.getenv("RADARR_URL", "").rstrip("/"),
            radarr_api_key=os.getenv("RADARR_API_KEY", ""),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30"))
        )
    
    def validate_service(self, service: str) -> bool:
        """Check if a service is properly configured"""
        if service == "sonarr":
            return bool(self.sonarr_url and self.sonarr_api_key)
        elif service == "radarr":
            return bool(self.radarr_url and self.radarr_api_key)
        return False


class APIClient:
    """Generic API client for Sonarr/Radarr"""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def get(self, endpoint: str, params: Optional[dict] = None) -> Any:
        """Make a GET request to the API"""
        url = f"{self.base_url}/api/v3/{endpoint}"
        headers = {"X-Api-Key": self.api_key}
        
        try:
            response = await self.client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"API request failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            raise
    
    async def post(self, endpoint: str, json_data: dict) -> Any:
        """Make a POST request to the API"""
        url = f"{self.base_url}/api/v3/{endpoint}"
        headers = {"X-Api-Key": self.api_key}
        
        try:
            response = await self.client.post(url, headers=headers, json=json_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"API request failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            raise
    
    async def put(self, endpoint: str, json_data: dict) -> Any:
        """Make a PUT request to the API"""
        url = f"{self.base_url}/api/v3/{endpoint}"
        headers = {"X-Api-Key": self.api_key}
        
        try:
            response = await self.client.put(url, headers=headers, json=json_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"API request failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            raise
    
    async def delete(self, endpoint: str) -> Any:
        """Make a DELETE request to the API"""
        url = f"{self.base_url}/api/v3/{endpoint}"
        headers = {"X-Api-Key": self.api_key}
        
        try:
            response = await self.client.delete(url, headers=headers)
            response.raise_for_status()
            return response.json() if response.text else {}
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"API request failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class SonarrRadarrMCP:
    """MCP Server for Sonarr and Radarr"""
    
    def __init__(self):
        self.config = Config.from_env()
        self.server = Server("mcp_servarr")
        self.sonarr_client: Optional[APIClient] = None
        self.radarr_client: Optional[APIClient] = None
        
        # Initialize clients if configured
        if self.config.validate_service("sonarr"):
            self.sonarr_client = APIClient(
                self.config.sonarr_url,
                self.config.sonarr_api_key,
                self.config.request_timeout
            )
            logger.info("Sonarr client initialized")
        
        if self.config.validate_service("radarr"):
            self.radarr_client = APIClient(
                self.config.radarr_url,
                self.config.radarr_api_key,
                self.config.request_timeout
            )
            logger.info("Radarr client initialized")
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """Register MCP handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools"""
            tools = []
            
            # Sonarr tools
            if self.sonarr_client:
                tools.extend([
                    Tool(
                        name="sonarr_get_recent_series",
                        description="Get recently added TV series from Sonarr. Returns series added in the last N days (default 7).",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "days": {
                                    "type": "number",
                                    "description": "Number of days to look back (default: 7)",
                                    "default": 7
                                }
                            }
                        }
                    ),
                    Tool(
                        name="sonarr_get_calendar",
                        description="Get upcoming episodes from Sonarr calendar. Shows episodes airing in the next N days.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "days": {
                                    "type": "number",
                                    "description": "Number of days to look ahead (default: 7)",
                                    "default": 7
                                }
                            }
                        }
                    ),
                    Tool(
                        name="sonarr_search_series",
                        description="Search for a TV series in Sonarr's library by title.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query (series title)"
                                }
                            },
                            "required": ["query"]
                        }
                    ),
                    Tool(
                        name="sonarr_get_system_status",
                        description="Get Sonarr system status including version, disk space, and health.",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="sonarr_get_queue",
                        description="Get current download queue in Sonarr.",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="sonarr_refresh_series",
                        description="Trigger a refresh of a specific series to update metadata and check for new episodes.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "series_id": {
                                    "type": "number",
                                    "description": "ID of the series to refresh"
                                }
                            },
                            "required": ["series_id"]
                        }
                    ),
                    Tool(
                        name="sonarr_search_episodes",
                        description="Trigger a search for missing episodes of a specific series.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "series_id": {
                                    "type": "number",
                                    "description": "ID of the series to search episodes for"
                                }
                            },
                            "required": ["series_id"]
                        }
                    )
                ])
            
            # Radarr tools
            if self.radarr_client:
                tools.extend([
                    Tool(
                        name="radarr_get_recent_movies",
                        description="Get recently added movies from Radarr. Returns movies added in the last N days (default 7).",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "days": {
                                    "type": "number",
                                    "description": "Number of days to look back (default: 7)",
                                    "default": 7
                                }
                            }
                        }
                    ),
                    Tool(
                        name="radarr_get_calendar",
                        description="Get upcoming movie releases from Radarr calendar.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "days": {
                                    "type": "number",
                                    "description": "Number of days to look ahead (default: 30)",
                                    "default": 30
                                }
                            }
                        }
                    ),
                    Tool(
                        name="radarr_search_movies",
                        description="Search for a movie in Radarr's library by title.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query (movie title)"
                                }
                            },
                            "required": ["query"]
                        }
                    ),
                    Tool(
                        name="radarr_get_system_status",
                        description="Get Radarr system status including version, disk space, and health.",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="radarr_get_queue",
                        description="Get current download queue in Radarr.",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="radarr_refresh_movie",
                        description="Trigger a refresh of a specific movie to update metadata.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "movie_id": {
                                    "type": "number",
                                    "description": "ID of the movie to refresh"
                                }
                            },
                            "required": ["movie_id"]
                        }
                    ),
                    Tool(
                        name="radarr_search_movie",
                        description="Trigger a search for a specific movie.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "movie_id": {
                                    "type": "number",
                                    "description": "ID of the movie to search for"
                                }
                            },
                            "required": ["movie_id"]
                        }
                    )
                ])
            
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls"""
            try:
                # Sonarr tools
                if name == "sonarr_get_recent_series":
                    if not self.sonarr_client:
                        return [TextContent(type="text", text="Sonarr is not configured")]
                    result = await self.get_recent_series(arguments.get("days", 7))
                    return [TextContent(type="text", text=result)]
                
                elif name == "sonarr_get_calendar":
                    if not self.sonarr_client:
                        return [TextContent(type="text", text="Sonarr is not configured")]
                    result = await self.get_sonarr_calendar(arguments.get("days", 7))
                    return [TextContent(type="text", text=result)]
                
                elif name == "sonarr_search_series":
                    if not self.sonarr_client:
                        return [TextContent(type="text", text="Sonarr is not configured")]
                    result = await self.search_sonarr_series(arguments["query"])
                    return [TextContent(type="text", text=result)]
                
                elif name == "sonarr_get_system_status":
                    if not self.sonarr_client:
                        return [TextContent(type="text", text="Sonarr is not configured")]
                    result = await self.get_sonarr_status()
                    return [TextContent(type="text", text=result)]
                
                elif name == "sonarr_get_queue":
                    if not self.sonarr_client:
                        return [TextContent(type="text", text="Sonarr is not configured")]
                    result = await self.get_sonarr_queue()
                    return [TextContent(type="text", text=result)]
                
                elif name == "sonarr_refresh_series":
                    if not self.sonarr_client:
                        return [TextContent(type="text", text="Sonarr is not configured")]
                    result = await self.refresh_sonarr_series(arguments["series_id"])
                    return [TextContent(type="text", text=result)]
                
                elif name == "sonarr_search_episodes":
                    if not self.sonarr_client:
                        return [TextContent(type="text", text="Sonarr is not configured")]
                    result = await self.search_sonarr_episodes(arguments["series_id"])
                    return [TextContent(type="text", text=result)]
                
                # Radarr tools
                elif name == "radarr_get_recent_movies":
                    if not self.radarr_client:
                        return [TextContent(type="text", text="Radarr is not configured")]
                    result = await self.get_recent_movies(arguments.get("days", 7))
                    return [TextContent(type="text", text=result)]
                
                elif name == "radarr_get_calendar":
                    if not self.radarr_client:
                        return [TextContent(type="text", text="Radarr is not configured")]
                    result = await self.get_radarr_calendar(arguments.get("days", 30))
                    return [TextContent(type="text", text=result)]
                
                elif name == "radarr_search_movies":
                    if not self.radarr_client:
                        return [TextContent(type="text", text="Radarr is not configured")]
                    result = await self.search_radarr_movies(arguments["query"])
                    return [TextContent(type="text", text=result)]
                
                elif name == "radarr_get_system_status":
                    if not self.radarr_client:
                        return [TextContent(type="text", text="Radarr is not configured")]
                    result = await self.get_radarr_status()
                    return [TextContent(type="text", text=result)]
                
                elif name == "radarr_get_queue":
                    if not self.radarr_client:
                        return [TextContent(type="text", text="Radarr is not configured")]
                    result = await self.get_radarr_queue()
                    return [TextContent(type="text", text=result)]
                
                elif name == "radarr_refresh_movie":
                    if not self.radarr_client:
                        return [TextContent(type="text", text="Radarr is not configured")]
                    result = await self.refresh_radarr_movie(arguments["movie_id"])
                    return [TextContent(type="text", text=result)]
                
                elif name == "radarr_search_movie":
                    if not self.radarr_client:
                        return [TextContent(type="text", text="Radarr is not configured")]
                    result = await self.search_radarr_movie(arguments["movie_id"])
                    return [TextContent(type="text", text=result)]
                
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
                    
            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    # Sonarr methods
    async def get_recent_series(self, days: int = 7) -> str:
        """Get recently added series"""
        series = await self.sonarr_client.get("series")
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent = []
        for show in series:
            added = datetime.fromisoformat(show["added"].replace("Z", "+00:00"))
            if added > cutoff_date:
                recent.append({
                    "title": show["title"],
                    "year": show.get("year"),
                    "added": show["added"],
                    "status": show["status"],
                    "network": show.get("network"),
                    "seasons": show.get("seasonCount", 0)
                })
        
        recent.sort(key=lambda x: x["added"], reverse=True)
        
        if not recent:
            return f"No series added in the last {days} days."
        
        result = f"Recently added series (last {days} days):\n\n"
        for show in recent:
            result += f"- {show['title']} ({show['year']})\n"
            result += f"  Added: {show['added']}\n"
            result += f"  Network: {show.get('network', 'Unknown')}\n"
            result += f"  Seasons: {show['seasons']}\n\n"
        
        return result
    
    async def get_sonarr_calendar(self, days: int = 7) -> str:
        """Get upcoming episodes"""
        start = datetime.now()
        end = start + timedelta(days=days)
        
        calendar = await self.sonarr_client.get(
            "calendar",
            params={
                "start": start.isoformat(),
                "end": end.isoformat()
            }
        )
        
        if not calendar:
            return f"No episodes airing in the next {days} days."
        
        result = f"Upcoming episodes (next {days} days):\n\n"
        for episode in calendar:
            air_date = episode.get("airDateUtc", "Unknown")
            result += f"- {episode['series']['title']} - S{episode['seasonNumber']:02d}E{episode['episodeNumber']:02d}\n"
            result += f"  Title: {episode.get('title', 'TBA')}\n"
            result += f"  Airs: {air_date}\n\n"
        
        return result
    
    async def search_sonarr_series(self, query: str) -> str:
        """Search for series"""
        series = await self.sonarr_client.get("series")
        matches = [s for s in series if query.lower() in s["title"].lower()]
        
        if not matches:
            return f"No series found matching '{query}'."
        
        result = f"Series matching '{query}':\n\n"
        for show in matches[:10]:  # Limit to 10 results
            result += f"- {show['title']} ({show.get('year', 'N/A')})\n"
            result += f"  Status: {show['status']}\n"
            result += f"  Seasons: {show.get('seasonCount', 0)}\n"
            result += f"  ID: {show['id']}\n\n"
        
        return result
    
    async def get_sonarr_status(self) -> str:
        """Get system status"""
        status = await self.sonarr_client.get("system/status")
        disk_space = await self.sonarr_client.get("diskspace")
        
        result = "Sonarr System Status:\n\n"
        result += f"Version: {status['version']}\n"
        result += f"OS: {status.get('osName', 'Unknown')}\n"
        result += f"Runtime: {status.get('runtimeName', 'Unknown')}\n\n"
        
        result += "Disk Space:\n"
        for disk in disk_space:
            free_gb = disk['freeSpace'] / (1024**3)
            total_gb = disk['totalSpace'] / (1024**3)
            result += f"- {disk['path']}: {free_gb:.2f} GB free of {total_gb:.2f} GB\n"
        
        return result
    
    async def get_sonarr_queue(self) -> str:
        """Get download queue"""
        queue = await self.sonarr_client.get("queue")
        
        if not queue.get("records"):
            return "Download queue is empty."
        
        result = "Current Download Queue:\n\n"
        for item in queue["records"]:
            result += f"- {item['series']['title']} - S{item['episode']['seasonNumber']:02d}E{item['episode']['episodeNumber']:02d}\n"
            result += f"  Status: {item['status']}\n"
            result += f"  Progress: {item.get('sizeleft', 0) / (1024**2):.2f} MB remaining\n\n"
        
        return result
    
    async def refresh_sonarr_series(self, series_id: int) -> str:
        """Refresh a series"""
        await self.sonarr_client.post(
            "command",
            {"name": "RefreshSeries", "seriesId": series_id}
        )
        return f"Refresh triggered for series ID {series_id}"
    
    async def search_sonarr_episodes(self, series_id: int) -> str:
        """Search for missing episodes"""
        await self.sonarr_client.post(
            "command",
            {"name": "SeriesSearch", "seriesId": series_id}
        )
        return f"Episode search triggered for series ID {series_id}"
    
    # Radarr methods
    async def get_recent_movies(self, days: int = 7) -> str:
        """Get recently added movies"""
        movies = await self.radarr_client.get("movie")
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent = []
        for movie in movies:
            added = datetime.fromisoformat(movie["added"].replace("Z", "+00:00"))
            if added > cutoff_date:
                recent.append({
                    "title": movie["title"],
                    "year": movie.get("year"),
                    "added": movie["added"],
                    "status": movie["status"],
                    "studio": movie.get("studio")
                })
        
        recent.sort(key=lambda x: x["added"], reverse=True)
        
        if not recent:
            return f"No movies added in the last {days} days."
        
        result = f"Recently added movies (last {days} days):\n\n"
        for movie in recent:
            result += f"- {movie['title']} ({movie['year']})\n"
            result += f"  Added: {movie['added']}\n"
            result += f"  Studio: {movie.get('studio', 'Unknown')}\n\n"
        
        return result
    
    async def get_radarr_calendar(self, days: int = 30) -> str:
        """Get upcoming movie releases"""
        start = datetime.now()
        end = start + timedelta(days=days)
        
        calendar = await self.radarr_client.get(
            "calendar",
            params={
                "start": start.isoformat(),
                "end": end.isoformat()
            }
        )
        
        if not calendar:
            return f"No movies releasing in the next {days} days."
        
        result = f"Upcoming movie releases (next {days} days):\n\n"
        for movie in calendar:
            result += f"- {movie['title']} ({movie.get('year', 'N/A')})\n"
            result += f"  Release: {movie.get('inCinemas', 'TBA')}\n"
            result += f"  Status: {movie['status']}\n\n"
        
        return result
    
    async def search_radarr_movies(self, query: str) -> str:
        """Search for movies"""
        movies = await self.radarr_client.get("movie")
        matches = [m for m in movies if query.lower() in m["title"].lower()]
        
        if not matches:
            return f"No movies found matching '{query}'."
        
        result = f"Movies matching '{query}':\n\n"
        for movie in matches[:10]:  # Limit to 10 results
            result += f"- {movie['title']} ({movie.get('year', 'N/A')})\n"
            result += f"  Status: {movie['status']}\n"
            result += f"  ID: {movie['id']}\n\n"
        
        return result
    
    async def get_radarr_status(self) -> str:
        """Get system status"""
        status = await self.radarr_client.get("system/status")
        disk_space = await self.radarr_client.get("diskspace")
        
        result = "Radarr System Status:\n\n"
        result += f"Version: {status['version']}\n"
        result += f"OS: {status.get('osName', 'Unknown')}\n"
        result += f"Runtime: {status.get('runtimeName', 'Unknown')}\n\n"
        
        result += "Disk Space:\n"
        for disk in disk_space:
            free_gb = disk['freeSpace'] / (1024**3)
            total_gb = disk['totalSpace'] / (1024**3)
            result += f"- {disk['path']}: {free_gb:.2f} GB free of {total_gb:.2f} GB\n"
        
        return result
    
    async def get_radarr_queue(self) -> str:
        """Get download queue"""
        queue = await self.radarr_client.get("queue")
        
        if not queue.get("records"):
            return "Download queue is empty."
        
        result = "Current Download Queue:\n\n"
        for item in queue["records"]:
            result += f"- {item['movie']['title']} ({item['movie'].get('year', 'N/A')})\n"
            result += f"  Status: {item['status']}\n"
            result += f"  Progress: {item.get('sizeleft', 0) / (1024**2):.2f} MB remaining\n\n"
        
        return result
    
    async def refresh_radarr_movie(self, movie_id: int) -> str:
        """Refresh a movie"""
        await self.radarr_client.post(
            "command",
            {"name": "RefreshMovie", "movieIds": [movie_id]}
        )
        return f"Refresh triggered for movie ID {movie_id}"
    
    async def search_radarr_movie(self, movie_id: int) -> str:
        """Search for a movie"""
        await self.radarr_client.post(
            "command",
            {"name": "MoviesSearch", "movieIds": [movie_id]}
        )
        return f"Search triggered for movie ID {movie_id}"
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.sonarr_client:
            await self.sonarr_client.close()
        if self.radarr_client:
            await self.radarr_client.close()


async def main():
    """Main entry point"""
    mcp = SonarrRadarrMCP()
    
    try:
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await mcp.server.run(
                read_stream,
                write_stream,
                mcp.server.create_initialization_options()
            )
    finally:
        await mcp.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
