from fastapi import HTTPException, Request
import httpx
from models import LocationResponse, WeatherResponse, ForecastResponse

OPENWEATHER_API_KEY = "26ca4d17ab7073188de43040d3cbaf93"

async def get_location_data(request: Request):
    try:
        forwarded_for = request.headers.get("x-forwarded-for")
        real_ip = request.headers.get("x-real-ip")
        client_ip = forwarded_for or real_ip or request.client.host
        
        if client_ip in ["127.0.0.1", "localhost", "::1"]:
            url = "http://ip-api.com/json/"
        else:
            url = f"http://ip-api.com/json/{client_ip}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get location: {str(e)}")

async def get_weather_data(lat: float, lon: float):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
        if data.get("cod") != 200:
            raise HTTPException(status_code=400, detail=data.get("message", "Weather data not found"))
            
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather data: {str(e)}")

async def get_forecast_data(lat: float, lon: float):
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
        if data.get("cod") != "200":
            raise HTTPException(status_code=400, detail=data.get("message", "Forecast data not found"))
            
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get forecast data: {str(e)}")

async def get_weather_by_city_data(city: str, country: str = None):
    try:
        query = f"{city},{country}" if country else city
        url = f"https://api.openweathermap.org/data/2.5/weather?q={query}&appid={OPENWEATHER_API_KEY}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
        if data.get("cod") != 200:
            raise HTTPException(status_code=400, detail=data.get("message", "City not found"))
            
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather data: {str(e)}")

async def get_forecast_by_city_data(city: str, country: str = None):
    try:
        query = f"{city},{country}" if country else city
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={query}&appid={OPENWEATHER_API_KEY}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
        if data.get("cod") != "200":
            raise HTTPException(status_code=400, detail=data.get("message", "City not found"))
            
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get forecast data: {str(e)}")