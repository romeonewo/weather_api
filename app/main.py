from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import weather, alerts

app = FastAPI(
    title="Weather API with Redis Caching",
    description="FastAPI application with OpenWeatherMap integration and optimized Redis caching",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(weather.router)
app.include_router(alerts.router)

@app.get("/")
async def root():
    return {
        "message": "Weather API with Redis Caching",
        "docs": "/docs",
        "endpoints": {
            "weather": "/weather/{city}",
            "alerts": "/alerts",
            "city_alerts": "/alerts/{city}"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "weather-api"}
