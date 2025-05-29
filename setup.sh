#!/bin/bash

echo "🚀 Setting up FastAPI Weather App with Redis Caching..."

# Create project directory structure
mkdir -p weather_api/{app/{models,services,routers},tests}

# Create __init__.py files
touch weather_api/app/__init__.py
touch weather_api/app/models/__init__.py
touch weather_api/app/services/__init__.py
touch weather_api/app/routers/__init__.py
touch weather_api/tests/__init__.py

cd weather_api

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
echo "⚙️ Setting up environment variables..."
cp .env.example .env
echo "❗ Please edit .env file and add your OpenWeatherMap API key"

# Start Redis with Docker
echo "🔴 Starting Redis server..."
docker-compose up -d redis

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file and add your OpenWeatherMap API key"
echo "2. Run: uvicorn app.main:app --reload"
echo "3. Visit: http://localhost:8000/docs for Swagger UI"
echo "4. Run tests: pytest"
