#!/usr/bin/env python3

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from typing import Optional
from datetime import datetime

# Assuming these are your own modules (make sure they exist and are correct)
from models import (
    LocationResponse,
    WeatherResponse,
    ForecastResponse,
    ErrorResponse
)

from services import (
    get_location_data,
    get_weather_data,
    get_forecast_data,
    get_weather_by_city_data,
    get_forecast_by_city_data
)

from templates import HTML_TEMPLATE

app = FastAPI(
    title="Location & Weather API",
    description="A comprehensive API for location detection and weather information.",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@weatherapi.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Demo routes
@app.get("/demo", response_class=HTMLResponse, tags=["Demo"], summary="Interactive Demo Interface")
async def demo():
    return HTML_TEMPLATE

@app.get("/", response_class=HTMLResponse, tags=["Demo"])
async def root():
    return HTML_TEMPLATE

# API Routes
@app.get("/api/location", response_model=LocationResponse, tags=["Location"])
async def get_location(request: Request):
    return await get_location_data(request)

@app.get("/api/weather", response_model=WeatherResponse, tags=["Weather"])
async def get_weather(lat: float, lon: float):
    return await get_weather_data(lat, lon)

@app.get("/api/forecast", response_model=ForecastResponse, tags=["Weather"])
async def get_forecast(lat: float, lon: float):
    return await get_forecast_data(lat, lon)

@app.get("/api/weather-by-city", response_model=WeatherResponse, tags=["Weather"])
async def get_weather_by_city(city: str, country: Optional[str] = None):
    return await get_weather_by_city_data(city, country)

@app.get("/api/forecast-by-city", response_model=ForecastResponse, tags=["Weather"])
async def get_forecast_by_city(city: str, country: Optional[str] = None):
    return await get_forecast_by_city_data(city, country)

# System endpoints
@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }

@app.get("/api/info", tags=["System"])
async def api_info():
    return {
        "api_name": "Location & Weather API",
        "version": "1.0.0",
        "description": "Professional API for location detection and weather information",
        "endpoints": {
            "location": {"path": "/api/location"},
            "weather": {"path": "/api/weather"},
            "forecast": {"path": "/api/forecast"},
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
