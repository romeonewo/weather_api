import requests
from datetime import datetime
from typing import List, Optional
from app.config import settings
from app.models.weather import WeatherData, WeatherAlert
from app.services.cache_service import cache_service

class WeatherService:
    def __init__(self):
        self.api_key = settings.openweather_api_key
        self.base_url = settings.openweather_base_url
    
    async def get_current_weather(self, city: str) -> WeatherData:
        """Get current weather for a city"""
        cache_key = f"weather:{city.lower()}"
        
        # Check cache first
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            return WeatherData(**cached_data)
        
        # Fetch from API
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        weather_data = WeatherData(
            city=data["name"],
            country=data["sys"]["country"],
            temperature=data["main"]["temp"],
            feels_like=data["main"]["feels_like"],
            humidity=data["main"]["humidity"],
            pressure=data["main"]["pressure"],
            description=data["weather"][0]["description"],
            wind_speed=data["wind"]["speed"],
            timestamp=datetime.now()
        )
        
        # Cache the result
        await cache_service.set(cache_key, weather_data.dict(), ttl=300)
        
        return weather_data
    
    async def get_weather_alerts(self, city: Optional[str] = None) -> List[WeatherAlert]:
        """Get weather alerts (mock data for demo - real implementation would use OpenWeather alerts API)"""
        cache_key = f"alerts:{city.lower() if city else 'global'}"
        
        # Check cache first
        cached_alerts = await cache_service.get(cache_key)
        if cached_alerts:
            return [WeatherAlert(**alert) for alert in cached_alerts]
        
        # Generate mock alerts (in real app, fetch from OpenWeather alerts API)
        mock_alerts = self._generate_mock_alerts(city)
        
        # Cache the alerts
        alerts_dict = [alert.dict() for alert in mock_alerts]
        await cache_service.set(cache_key, alerts_dict, ttl=settings.cache_ttl)
        
        return mock_alerts
    
    def _generate_mock_alerts(self, city: Optional[str] = None) -> List[WeatherAlert]:
        """Generate mock weather alerts for demo purposes"""
        alerts = []
        
        if city:
            alerts.append(WeatherAlert(
                id=f"alert_{city.lower()}_001",
                city=city,
                alert_type="temperature",
                severity="moderate",
                description=f"High temperature warning for {city}",
                start_time=datetime.now()
            ))
        else:
            # Global alerts
            cities = ["London", "New York", "Tokyo", "Sydney"]
            for i, city_name in enumerate(cities):
                alerts.append(WeatherAlert(
                    id=f"alert_global_{i+1:03d}",
                    city=city_name,
                    alert_type="wind" if i % 2 == 0 else "rain",
                    severity="high" if i % 3 == 0 else "moderate",
                    description=f"Weather alert for {city_name}",
                    start_time=datetime.now()
                ))
        
        return alerts

weather_service = WeatherService()
