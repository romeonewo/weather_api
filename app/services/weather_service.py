import httpx
from datetime import datetime
from typing import List, Optional, Tuple
from app.config import settings
from app.models.weather import WeatherData, WeatherAlert
from app.services.cache_service import cache_service

class WeatherService:
    def __init__(self):
        self.api_key = settings.openweather_api_key
        self.base_url = settings.openweather_base_url
        self.geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
    
    async def _get_coordinates(self, city: str) -> Tuple[float, float]:
        """Get lat/lon coordinates for a city using OpenWeather Geocoding API"""
        cache_key = f"geocoding:{city.lower()}"
        
        # Check cache first
        cached_coords = await cache_service.get(cache_key)
        if cached_coords:
            return cached_coords['lat'], cached_coords['lon']
        
        # Fetch coordinates from Geocoding API
        params = {
            "q": city,
            "limit": 1,
            "appid": self.api_key
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self.geocoding_url, params=params)
            response.raise_for_status()
            data = response.json()
        
        if not data:
            raise ValueError(f"City '{city}' not found")
        
        lat, lon = data[0]["lat"], data[0]["lon"]
        
        # Cache coordinates for 24 hours (they don't change often)
        await cache_service.set(cache_key, {"lat": lat, "lon": lon}, ttl=86400)
        
        return lat, lon
    
    async def get_current_weather(self, city: str) -> WeatherData:
        """Get current weather for a city"""
        cache_key = f"weather:{city.lower()}"
        
        # Check cache first
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            return WeatherData(**cached_data)
        
        try:
            # Get coordinates for the city
            lat, lon = await self._get_coordinates(city)
            
            # Fetch weather data using lat/lon (the recommended approach)
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
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
            
        except ValueError as e:
            # City not found
            raise e
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Weather data not found for {city}")
            raise e
        except Exception as e:
            raise Exception(f"Failed to fetch weather data: {str(e)}")
    
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
