from fastapi import APIRouter, HTTPException
from app.models.weather import WeatherData
from app.services.weather_service import weather_service

router = APIRouter(prefix="/weather", tags=["Weather"])

@router.get("/{city}", response_model=WeatherData)
async def get_weather(city: str):
    """Get current weather for a specific city"""
    try:
        weather_data = await weather_service.get_current_weather(city)
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Weather data not found for {city}: {str(e)}")
