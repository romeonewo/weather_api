from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    openweather_api_key: str
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 300  # 5 minutes
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"
    
    class Config:
        env_file = ".env"

settings = Settings()
