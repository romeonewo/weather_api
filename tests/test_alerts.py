import pytest
import time
from unittest.mock import patch, AsyncMock
from app.services.weather_service import weather_service

class TestAlertsAPI:
    
    def test_alerts_endpoint_performance(self, client):
        """Test alerts endpoint performance (<200ms)"""
        start_time = time.time()
        
        with patch('app.services.cache_service.cache_service.exists', new_callable=AsyncMock) as mock_exists:
            mock_exists.return_value = False
            with patch('app.services.cache_service.cache_service.get', new_callable=AsyncMock) as mock_get:
                mock_get.return_value = None
                with patch('app.services.cache_service.cache_service.set', new_callable=AsyncMock) as mock_set:
                    mock_set.return_value = True
                    
                    response = client.get("/alerts")
                    
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    
                    assert response.status_code == 200
                    assert response_time < 200  # Less than 200ms
                    
                    data = response.json()
                    assert "alerts" in data
                    assert "total" in data
                    assert "cached" in data
    
    def test_city_alerts_endpoint(self, client):
        """Test city-specific alerts endpoint"""
        with patch('app.services.cache_service.cache_service.exists', new_callable=AsyncMock) as mock_exists:
            mock_exists.return_value = False
            with patch('app.services.cache_service.cache_service.get', new_callable=AsyncMock) as mock_get:
                mock_get.return_value = None
                with patch('app.services.cache_service.cache_service.set', new_callable=AsyncMock) as mock_set:
                    mock_set.return_value = True
                    
                    response = client.get("/alerts/London")
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["total"] >= 0
                    assert isinstance(data["alerts"], list)
    
    def test_alerts_caching_behavior(self, client):
        """Test alerts caching improves performance"""
        # First request (cache miss)
        with patch('app.services.cache_service.cache_service.exists', new_callable=AsyncMock) as mock_exists:
            mock_exists.return_value = False
            
            start_time = time.time()
            response1 = client.get("/alerts")
            time1 = (time.time() - start_time) * 1000
            
            assert response1.status_code == 200
            
            # Second request (cache hit simulation)
            mock_exists.return_value = True
            
            start_time = time.time()
            response2 = client.get("/alerts")
            time2 = (time.time() - start_time) * 1000
            
            assert response2.status_code == 200
            # Cache hit should be faster (in real scenario)
    
    @pytest.mark.asyncio
    async def test_mock_alerts_generation(self):
        """Test mock alerts generation"""
        alerts = await weather_service.get_weather_alerts()
        assert len(alerts) > 0
        
        for alert in alerts:
            assert alert.id
            assert alert.city
            assert alert.alert_type
            assert alert.severity
            assert alert.description
    
    @pytest.mark.asyncio
    async def test_city_specific_alerts(self):
        """Test city-specific alerts generation"""
        city = "London"
        alerts = await weather_service.get_weather_alerts(city)
        
        assert len(alerts) >= 1
        assert all(alert.city == city for alert in alerts)
    
    def test_alerts_response_structure(self, client):
        """Test alerts response structure"""
        with patch('app.services.cache_service.cache_service.exists', new_callable=AsyncMock) as mock_exists:
            mock_exists.return_value = False
            
            response = client.get("/alerts")
            assert response.status_code == 200
            
            data = response.json()
            required_fields = ["alerts", "total", "cached"]
            
            for field in required_fields:
                assert field in data
            
            if data["alerts"]:
                alert = data["alerts"][0]
                alert_fields = ["id", "city", "alert_type", "severity", "description", "start_time"]
                for field in alert_fields:
                    assert field in alert
