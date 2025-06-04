from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import httpx
from datetime import datetime

# Pydantic models for API documentation
class LocationResponse(BaseModel):
    status: str = Field(..., description="Status of the request (success/fail)")
    country: Optional[str] = Field(None, description="Country name")
    countryCode: Optional[str] = Field(None, description="Country code")
    region: Optional[str] = Field(None, description="Region code")
    regionName: Optional[str] = Field(None, description="Region name")
    city: Optional[str] = Field(None, description="City name")
    zip: Optional[str] = Field(None, description="ZIP/Postal code")
    lat: Optional[float] = Field(None, description="Latitude")
    lon: Optional[float] = Field(None, description="Longitude")
    timezone: Optional[str] = Field(None, description="Timezone")
    isp: Optional[str] = Field(None, description="Internet service provider")
    org: Optional[str] = Field(None, description="Organization")
    as_: Optional[str] = Field(None, alias="as", description="AS number and organization")
    query: Optional[str] = Field(None, description="IP address used for the query")
    message: Optional[str] = Field(None, description="Error message if status is fail")

class WeatherCondition(BaseModel):
    id: int = Field(..., description="Weather condition ID")
    main: str = Field(..., description="Group of weather parameters (Rain, Snow, Extreme etc.)")
    description: str = Field(..., description="Weather condition description")
    icon: str = Field(..., description="Weather icon ID")

class MainWeather(BaseModel):
    temp: float = Field(..., description="Temperature in Kelvin")
    feels_like: float = Field(..., description="Human perception of weather in Kelvin")
    temp_min: float = Field(..., description="Minimum temperature in Kelvin")
    temp_max: float = Field(..., description="Maximum temperature in Kelvin")
    pressure: int = Field(..., description="Atmospheric pressure in hPa")
    humidity: int = Field(..., description="Humidity percentage")
    sea_level: Optional[int] = Field(None, description="Atmospheric pressure on sea level in hPa")
    grnd_level: Optional[int] = Field(None, description="Atmospheric pressure on ground level in hPa")

class WindInfo(BaseModel):
    speed: float = Field(..., description="Wind speed in meter/sec")
    deg: Optional[int] = Field(None, description="Wind direction in degrees")
    gust: Optional[float] = Field(None, description="Wind gust in meter/sec")

class CloudsInfo(BaseModel):
    all: int = Field(..., description="Cloudiness percentage")

class WeatherResponse(BaseModel):
    coord: dict = Field(..., description="Coordinates")
    weather: List[WeatherCondition] = Field(..., description="Weather conditions")
    base: str = Field(..., description="Internal parameter")
    main: MainWeather = Field(..., description="Main weather data")
    visibility: Optional[int] = Field(None, description="Visibility in meters")
    wind: Optional[WindInfo] = Field(None, description="Wind information")
    clouds: Optional[CloudsInfo] = Field(None, description="Clouds information")
    dt: int = Field(..., description="Time of data calculation, unix timestamp")
    sys: dict = Field(..., description="System data")
    timezone: int = Field(..., description="Shift in seconds from UTC")
    id: int = Field(..., description="City ID")
    name: str = Field(..., description="City name")
    cod: int = Field(..., description="Internal parameter")

class ForecastItem(BaseModel):
    dt: int = Field(..., description="Time of data forecasted, unix timestamp")
    main: MainWeather = Field(..., description="Main weather data")
    weather: List[WeatherCondition] = Field(..., description="Weather conditions")
    clouds: Optional[CloudsInfo] = Field(None, description="Clouds information")
    wind: Optional[WindInfo] = Field(None, description="Wind information")
    visibility: Optional[int] = Field(None, description="Visibility in meters")
    pop: Optional[float] = Field(None, description="Probability of precipitation")
    sys: Optional[dict] = Field(None, description="System data")
    dt_txt: str = Field(..., description="Time of data forecasted, ISO format")

class ForecastResponse(BaseModel):
    cod: str = Field(..., description="Internal parameter")
    message: int = Field(..., description="Internal parameter")
    cnt: int = Field(..., description="Number of forecast items")
    list: List[ForecastItem] = Field(..., description="List of forecast items")
    city: dict = Field(..., description="City information")

class ErrorResponse(BaseModel):
    cod: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")

# Initialize FastAPI app with proper metadata
app = FastAPI(
    title="Location & Weather API",
    description="""
    A comprehensive API for location detection and weather information.
    
    ## Features
    
    * **Location Detection**: Get location information based on IP address
    * **Current Weather**: Get current weather conditions for any location
    * **Weather Forecast**: Get 5-day weather forecast with 3-hour intervals
    * **City-based Weather**: Get weather data using city names
    
    ## API Endpoints
    
    - `/api/location` - Get location information based on IP
    - `/api/weather` - Get current weather by coordinates
    - `/api/forecast` - Get weather forecast by coordinates
    - `/api/weather-by-city` - Get current weather by city name
    - `/api/forecast-by-city` - Get weather forecast by city name
    - `/api/health` - Health check endpoint
    - `/api/info` - API information and usage guidelines
    
    ## Authentication
    
    No authentication required for basic usage.
    
    ## Rate Limits
    
    Please be respectful with API usage. Excessive requests may be throttled.
    """,
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

# Root endpoint redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation"""
    return {"message": "Welcome to Location & Weather API", "documentation": "/docs", "redoc": "/redoc"}

# API Routes
@app.get(
    "/api/location",
    response_model=LocationResponse,
    tags=["Location"],
    summary="Get Location Information",
    description="Detect location information based on the client's IP address. Returns country, region, city, coordinates, and other location data."
)
async def get_location(request: Request):
    """
    Get location information based on IP address.
    
    This endpoint automatically detects the client's location using their IP address.
    It provides comprehensive location data including:
    - Geographic coordinates (latitude/longitude)
    - City, region, and country information
    - Timezone and ISP details
    
    **Note**: For localhost requests, it will detect the server's public IP location.
    """
    try:
        # Get client IP - try different methods
        forwarded_for = request.headers.get("x-forwarded-for")
        real_ip = request.headers.get("x-real-ip")
        client_ip = forwarded_for or real_ip or request.client.host
        
        # If running locally, use empty query to get current IP
        if client_ip in ["127.0.0.1", "localhost", "::1"]:
            url = "http://ip-api.com/json/"
        else:
            url = f"http://ip-api.com/json/{client_ip}"
        
        # Call IP-API
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get location: {str(e)}")

@app.get(
    "/api/weather",
    response_model=WeatherResponse,
    responses={400: {"model": ErrorResponse}},
    tags=["Weather"],
    summary="Get Current Weather",
    description="Get current weather conditions for a specific location using latitude and longitude coordinates."
)
async def get_weather(
    lat: float = Query(..., description="Latitude coordinate", example=40.7128),
    lon: float = Query(..., description="Longitude coordinate", example=-74.0060)
):
    """
    Get current weather conditions for a specific location.
    
    This endpoint provides comprehensive current weather data including:
    - Temperature (current, feels like, min/max)
    - Weather conditions and descriptions
    - Humidity, pressure, and visibility
    - Wind speed and direction
    - Cloud coverage
    
    **Parameters:**
    - **lat**: Latitude coordinate (required)
    - **lon**: Longitude coordinate (required)
    
    **Example:** `/api/weather?lat=40.7128&lon=-74.0060` (New York City)
    """
    try:
        api_key = "26ca4d17ab7073188de43040d3cbaf93"
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
        if data.get("cod") != 200:
            raise HTTPException(status_code=400, detail=data.get("message", "Weather data not found"))
            
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather data: {str(e)}")

@app.get(
    "/api/forecast",
    response_model=ForecastResponse,
    responses={400: {"model": ErrorResponse}},
    tags=["Weather"],
    summary="Get Weather Forecast",
    description="Get 5-day weather forecast with 3-hour intervals for a specific location using latitude and longitude coordinates."
)
async def get_forecast(
    lat: float = Query(..., description="Latitude coordinate", example=40.7128),
    lon: float = Query(..., description="Longitude coordinate", example=-74.0060)
):
    """
    Get 5-day weather forecast with 3-hour intervals.
    
    This endpoint provides detailed weather forecast data including:
    - 5-day forecast with 3-hour intervals
    - Temperature predictions (current, min/max)
    - Weather conditions for each time period
    - Precipitation probability
    - Wind and atmospheric conditions
    
    **Parameters:**
    - **lat**: Latitude coordinate (required)
    - **lon**: Longitude coordinate (required)
    
    **Example:** `/api/forecast?lat=40.7128&lon=-74.0060` (New York City)
    
    **Response contains:**
    - `list`: Array of forecast items (up to 40 items for 5 days)
    - `city`: City information including name, coordinates, and timezone
    - Each forecast item includes weather, temperature, and atmospheric data
    """
    try:
        api_key = "26ca4d17ab7073188de43040d3cbaf93"
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
        if data.get("cod") != "200":
            raise HTTPException(status_code=400, detail=data.get("message", "Forecast data not found"))
            
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get forecast data: {str(e)}")

@app.get(
    "/api/weather-by-city",
    response_model=WeatherResponse,
    responses={400: {"model": ErrorResponse}},
    tags=["Weather"],
    summary="Get Weather by City Name",
    description="Get current weather conditions by city name instead of coordinates."
)
async def get_weather_by_city(
    city: str = Query(..., description="City name", example="New York"),
    country: Optional[str] = Query(None, description="Country code (optional)", example="US")
):
    """
    Get current weather conditions by city name.
    
    This is a convenience endpoint that allows you to get weather data using
    city names instead of coordinates.
    
    **Parameters:**
    - **city**: City name (required)
    - **country**: Country code (optional, helps with accuracy)
    
    **Examples:**
    - `/api/weather-by-city?city=London`
    - `/api/weather-by-city?city=London&country=GB`
    - `/api/weather-by-city?city=New York&country=US`
    """
    try:
        api_key = "26ca4d17ab7073188de43040d3cbaf93"
        
        if country:
            query = f"{city},{country}"
        else:
            query = city
            
        url = f"https://api.openweathermap.org/data/2.5/weather?q={query}&appid={api_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
        if data.get("cod") != 200:
            raise HTTPException(status_code=400, detail=data.get("message", "City not found"))
            
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather data: {str(e)}")

@app.get(
    "/api/forecast-by-city",
    response_model=ForecastResponse,
    responses={400: {"model": ErrorResponse}},
    tags=["Weather"],
    summary="Get Forecast by City Name",
    description="Get 5-day weather forecast by city name instead of coordinates."
)
async def get_forecast_by_city(
    city: str = Query(..., description="City name", example="New York"),
    country: Optional[str] = Query(None, description="Country code (optional)", example="US")
):
    """
    Get 5-day weather forecast by city name.
    
    This is a convenience endpoint that allows you to get forecast data using
    city names instead of coordinates.
    
    **Parameters:**
    - **city**: City name (required)
    - **country**: Country code (optional, helps with accuracy)
    
    **Examples:**
    - `/api/forecast-by-city?city=Tokyo`
    - `/api/forecast-by-city?city=Paris&country=FR`
    """
    try:
        api_key = "26ca4d17ab7073188de43040d3cbaf93"
        
        if country:
            query = f"{city},{country}"
        else:
            query = city
            
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={query}&appid={api_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
        if data.get("cod") != "200":
            raise HTTPException(status_code=400, detail=data.get("message", "City not found"))
            
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get forecast data: {str(e)}")

@app.get(
    "/api/health",
    tags=["System"],
    summary="Health Check",
    description="Check if the API is running and healthy."
)
async def health_check():
    """
    Health check endpoint to verify API status.
    
    Returns basic system information and API status.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "message": "Location & Weather API is running successfully"
    }

@app.get(
    "/api/info",
    tags=["System"],
    summary="API Information",
    description="Get information about API endpoints and usage."
)
async def api_info():
    """
    Get comprehensive API information and usage guidelines.
    
    Returns information about all available endpoints, rate limits,
    and usage examples.
    """
    return {
        "api_name": "Location & Weather API",
        "version": "1.0.0",
        "description": "Professional API for location detection and weather information",
        "endpoints": {
            "location": {
                "path": "/api/location",
                "method": "GET",
                "description": "Get location information based on IP address",
                "parameters": "None (automatic IP detection)"
            },
            "weather": {
                "path": "/api/weather",
                "method": "GET",
                "description": "Get current weather by coordinates",
                "parameters": "lat (float), lon (float)"
            },
            "forecast": {
                "path": "/api/forecast",
                "method": "GET",
                "description": "Get 5-day weather forecast by coordinates",
                "parameters": "lat (float), lon (float)"
            },
            "weather_by_city": {
                "path": "/api/weather-by-city",
                "method": "GET",
                "description": "Get current weather by city name",
                "parameters": "city (string), country (string, optional)"
            },
            "forecast_by_city": {
                "path": "/api/forecast-by-city",
                "method": "GET",
                "description": "Get forecast by city name",
                "parameters": "city (string), country (string, optional)"
            }
        },
        "documentation_urls": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "data_sources": {
            "location": "ip-api.com",
            "weather": "OpenWeatherMap API"
        },
        "usage_examples": {
            "get_location": "GET /api/location",
            "get_weather": "GET /api/weather?lat=40.7128&lon=-74.0060",
            "get_forecast": "GET /api/forecast?lat=40.7128&lon=-74.0060",
            "get_weather_by_city": "GET /api/weather-by-city?city=New York&country=US"
        }
    }

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        app, 
        host="0.0.0.0",
        port=port,
        title="Location & Weather API",
        description="Professional API with Swagger documentation"
    )