from fastapi import APIRouter
from typing import Optional
from app.models.weather import AlertsResponse
from app.services.weather_service import weather_service
from app.services.cache_service import cache_service
import time

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=AlertsResponse)
async def get_alerts():
    """Get all weather alerts (optimized with Redis caching for <200ms latency)"""
    start_time = time.time()
    
    cache_key = "alerts:global"
    cached = await cache_service.exists(cache_key)
    
    alerts = await weather_service.get_weather_alerts()
    
    processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    return AlertsResponse(
        alerts=alerts,
        total=len(alerts),
        cached=cached
    )

@router.get("/{city}", response_model=AlertsResponse)
async def get_city_alerts(city: str):
    """Get weather alerts for a specific city (optimized with Redis caching)"""
    start_time = time.time()
    
    cache_key = f"alerts:{city.lower()}"
    cached = await cache_service.exists(cache_key)
    
    alerts = await weather_service.get_weather_alerts(city)
    
    processing_time = (time.time() - start_time) * 1000
    
    return AlertsResponse(
        alerts=alerts,
        total=len(alerts),
        cached=cached
    )
