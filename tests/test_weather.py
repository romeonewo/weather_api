import pytest
from unittest.mock import patch, AsyncMock
import requests_mock
from app.services.weather_service import weather_service
from app.models.weather import WeatherData

class TestWeatherAPI:
    
    def test_weather_endpoint_success(self, client, sample_weather_response):
        """Test successful weather API call"""
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.openweathermap.org/data/2.5/weather",
                json=sample_weather_response
            )
            
            with patch('app.services.cache_service.cache_service.get', new_callable=AsyncMock) as mock_get:
                mock_get.return_value = None
                with patch('app.services.cache_service.cache_service.set', new_callable=AsyncMock) as mock_set:
                    mock_set.return_value = True
                    
                    response = client.get("/weather/London")
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["city"] == "London"
                    assert data["country"] == "GB"
                    assert data["temperature"] == 15.5
    
    def test_weather_endpoint_city_not_found(self, client):
        """Test weather API with invalid city"""
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.openweathermap.org/data/2.5/weather",
                status_code=404,
                json={"message": "city not found"}
            )
            
            response = client.get("/weather/InvalidCity")
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_weather_service_caching(self, mock_cache_service, sample_weather_response):
        """Test weather service caching functionality"""
        # Test cache miss then hit
        mock_cache_service.get.return_value = None
        
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.openweathermap.org/data/2.5/weather",
                json=sample_weather_response
            )
            
            # First call - cache miss
            result1 = await weather_service.get_current_weather("London")
            assert result1.city == "London"
            
            # Simulate cache hit
            cached_data = {
                "city": "London",
                "country": "GB",
                "temperature": 15.5,
                "feels_like": 14.2,
                "humidity": 80,
                "pressure": 1013,
                "description": "cloudy",
                "wind_speed": 5.2,
                "timestamp": "2024-01-01T12:00:00"
            }
            mock_cache_service.get.return_value = cached_data
            
            # Second call - cache hit
            result2 = await weather_service.get_current_weather("London")
            assert result2.city == "London"
    
    def test_swagger_documentation(self, client):
        """Test that Swagger UI is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
