"""
Tests for Sonarr Radarr MCP Server
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.server import APIClient, Config


class TestConfig:
    """Test configuration loading"""
    
    def test_config_from_env(self, monkeypatch):
        """Test loading config from environment variables"""
        monkeypatch.setenv("SONARR_URL", "http://sonarr:8989")
        monkeypatch.setenv("SONARR_API_KEY", "test-key")
        monkeypatch.setenv("RADARR_URL", "http://radarr:7878")
        monkeypatch.setenv("RADARR_API_KEY", "test-key-2")
        
        config = Config.from_env()
        
        assert config.sonarr_url == "http://sonarr:8989"
        assert config.sonarr_api_key == "test-key"
        assert config.radarr_url == "http://radarr:7878"
        assert config.radarr_api_key == "test-key-2"
    
    def test_validate_service_sonarr(self):
        """Test service validation for Sonarr"""
        config = Config(
            sonarr_url="http://sonarr:8989",
            sonarr_api_key="test-key"
        )
        
        assert config.validate_service("sonarr") is True
        assert config.validate_service("radarr") is False
    
    def test_validate_service_radarr(self):
        """Test service validation for Radarr"""
        config = Config(
            radarr_url="http://radarr:7878",
            radarr_api_key="test-key"
        )
        
        assert config.validate_service("sonarr") is False
        assert config.validate_service("radarr") is True


class TestAPIClient:
    """Test API client"""
    
    @pytest.mark.asyncio
    async def test_api_client_get(self):
        """Test GET request"""
        client = APIClient("http://test:8989", "test-key")
        
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"test": "data"}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response
            
            result = await client.get("series")
            
            assert result == {"test": "data"}
            mock_get.assert_called_once()
        
        await client.close()
    
    @pytest.mark.asyncio
    async def test_api_client_post(self):
        """Test POST request"""
        client = APIClient("http://test:8989", "test-key")
        
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"success": True}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response
            
            result = await client.post("command", {"name": "test"})
            
            assert result == {"success": True}
            mock_post.assert_called_once()
        
        await client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
