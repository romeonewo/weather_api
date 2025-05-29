from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class WeatherData(BaseModel):
    city: str
    country: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    description: str
    wind_speed: float
    timestamp: datetime

class WeatherAlert(BaseModel):
    id: str
    city: str
    alert_type: str
    severity: str
    description: str
    start_time: datetime
    end_time: Optional[datetime] = None
    
class AlertsResponse(BaseModel):
    alerts: List[WeatherAlert]
    total: int
    cached: bool = False
