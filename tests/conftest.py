import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.services.cache_service import cache_service
from app.services.weather_service import weather_service

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_cache_service():
    cache_service.get = AsyncMock(return_value=None)
    cache_service.set = AsyncMock(return_value=True)
    cache_service.exists = AsyncMock(return_value=False)
    cache_service.delete = AsyncMock(return_value=True)
    return cache_service

@pytest.fixture
def mock_weather_service():
    return weather_service

@pytest.fixture
def sample_weather_response():
    return {
        "name": "London",
        "sys": {"country": "GB"},
        "main": {
            "temp": 15.5,
            "feels_like": 14.2,
            "humidity": 80,
            "pressure": 1013
        },
        "weather": [{"description": "cloudy"}],
        "wind": {"speed": 5.2}
    }
