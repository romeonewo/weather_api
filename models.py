from pydantic import BaseModel, Field
from typing import Optional, List

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