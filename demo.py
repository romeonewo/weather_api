from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
import json
from datetime import datetime, timedelta

app = FastAPI(title="Location & Weather Demo")

# HTML template as a string for simplicity
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Location & Weather Demo</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #a8e6cf 0%, #dcedc1 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            padding: 30px;
        }
        
        h1 {
            text-align: center;
            color: #2d5a3d;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        
        .button {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 16px;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
            margin: 10px;
        }
        
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
        }
        
        .button:disabled {
            background: #cccccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .info-box {
            background: #f8fff8;
            border: 2px solid #4CAF50;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .location-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 15px 0;
        }
        
        .info-item {
            background: white;
            padding: 10px;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }
        
        .info-label {
            font-weight: bold;
            color: #2d5a3d;
        }
        
        #map {
            height: 400px;
            width: 100%;
            border-radius: 10px;
            margin: 20px 0;
            border: 2px solid #4CAF50;
        }
        
        .weather-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .weather-card {
            background: linear-gradient(135deg, #e8f5e8, #f0f8f0);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #4CAF50;
        }
        
        .weather-icon {
            font-size: 2em;
            margin-bottom: 10px;
        }
        
        .loading {
            text-align: center;
            color: #4CAF50;
            font-style: italic;
        }
        
        .error {
            color: #d32f2f;
            background: #ffebee;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        /* Forecast styles */
        .forecast-container {
            margin-top: 30px;
        }
        
        .forecast-header {
            text-align: center;
            margin-bottom: 20px;
            color: #2d5a3d;
            font-size: 1.5em;
        }
        
        .forecast-days {
            display: flex;
            overflow-x: auto;
            gap: 15px;
            padding: 10px 0;
        }
        
        .forecast-day {
            min-width: 150px;
            background: linear-gradient(135deg, #e8f5e8, #f0f8f0);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #4CAF50;
        }
        
        .forecast-date {
            font-weight: bold;
            margin-bottom: 10px;
            color: #2d5a3d;
        }
        
        .forecast-temp {
            margin: 5px 0;
        }
        
        .forecast-description {
            font-size: 0.9em;
            color: #555;
        }
        
        /* Scrollbar styling */
        .forecast-days::-webkit-scrollbar {
            height: 8px;
        }
        
        .forecast-days::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        .forecast-days::-webkit-scrollbar-thumb {
            background: #4CAF50;
            border-radius: 10px;
        }
        
        .forecast-days::-webkit-scrollbar-thumb:hover {
            background: #45a049;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 Location & Weather Demo</h1>
        
        <div style="text-align: center;">
            <button class="button" onclick="getCurrentLocation()">📍 Get Current Location</button>
        </div>
        
        <div id="locationResult">
            <div class="info-box">
                <h3>📍 Your Location</h3>
                <div class="location-info">
                    <div class="info-item">
                        <div class="info-label">City</div>
                        <div id="city">Click "Get Current Location" first</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Region</div>
                        <div id="region">Click "Get Current Location" first</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Latitude</div>
                        <div id="latitude">Click "Get Current Location" first</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Longitude</div>
                        <div id="longitude">Click "Get Current Location" first</div>
                    </div>
                </div>
            </div>
            
            <div id="map"></div>
            
            <div style="text-align: center;">
                <button class="button" onclick="getWeatherCondition()" id="weatherBtn">🌤️ Get Weather Condition</button>
                <button class="button" onclick="getWeatherForecast()" id="forecastBtn">📅 Get Weather Forecast</button>
            </div>
        </div>
        
        <div id="weatherResult">
            <div class="info-box">
                <h3>🌤️ Current Weather</h3>
                <div id="weatherContent">
                    <p style="text-align: center; color: #666;">Click "Get Weather Condition" to see weather data</p>
                </div>
                <div class="weather-info" id="weatherCards">
                    <div class="weather-card">
                        <div class="weather-icon" id="weatherIcon"></div>
                        <div class="info-label">Condition</div>
                        <div id="weatherMain"></div>
                        <div id="weatherDesc"></div>
                    </div>
                    <div class="weather-card">
                        <div class="weather-icon">🌡️</div>
                        <div class="info-label">Temperature</div>
                        <div id="temperature"></div>
                        <div>Feels like: <span id="feelsLike"></span></div>
                    </div>
                    <div class="weather-card">
                        <div class="weather-icon">💧</div>
                        <div class="info-label">Humidity</div>
                        <div id="humidity"></div>
                    </div>
                    <div class="weather-card">
                        <div class="weather-icon">🌬️</div>
                        <div class="info-label">Wind</div>
                        <div id="windSpeed"></div>
                        <div>Direction: <span id="windDirection"></span>°</div>
                    </div>
                </div>
            </div>
            
            <div id="forecastResult" class="info-box" style="display: none;">
                <h3>📅 Weather Forecast</h3>
                <div id="forecastContent">
                    <p style="text-align: center; color: #666;">Click "Get Weather Forecast" to see weather predictions</p>
                </div>
                <div class="forecast-container">
                    <div class="forecast-header">5-Day Weather Forecast</div>
                    <div class="forecast-days" id="forecastDays"></div>
                </div>
            </div>
        </div>
        
        <div id="loading" class="loading" style="display: none;">
            Loading... Please wait
        </div>
        
        <div id="error" class="error" style="display: none;"></div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        let map;
        let currentLat, currentLon;
        
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
        }
        
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }
        
        async function getCurrentLocation() {
            showLoading();
            try {
                const response = await fetch('/get-location');
                const data = await response.json();
                
                console.log('Location data received:', data); // Debug log
                
                if (data.status === 'success' || data.lat) {
                    // Display location info
                    document.getElementById('city').textContent = data.city || 'Unknown';
                    document.getElementById('region').textContent = data.regionName || data.region || 'Unknown';
                    document.getElementById('latitude').textContent = data.lat ? data.lat.toFixed(6) : 'Unknown';
                    document.getElementById('longitude').textContent = data.lon ? data.lon.toFixed(6) : 'Unknown';
                    
                    // Store coordinates
                    currentLat = data.lat;
                    currentLon = data.lon;
                    
                    // Initialize map if coordinates exist
                    if (data.lat && data.lon) {
                        initMap(data.lat, data.lon, data.city || 'Your Location');
                    }
                } else {
                    showError('Failed to get location information. Response: ' + JSON.stringify(data));
                }
            } catch (error) {
                showError('Error getting location: ' + error.message);
            }
            hideLoading();
        }
        
        function initMap(lat, lon, city) {
            if (map) {
                map.remove();
            }
            
            map = L.map('map').setView([lat, lon], 13);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            L.marker([lat, lon]).addTo(map)
                .bindPopup(`📍 ${city}<br>Lat: ${lat.toFixed(4)}, Lon: ${lon.toFixed(4)}`)
                .openPopup();
        }
        
        async function getWeatherCondition() {
            if (!currentLat || !currentLon) {
                showError('Please get your location first');
                return;
            }
            
            showLoading();
            try {
                const response = await fetch(`/get-weather?lat=${currentLat}&lon=${currentLon}`);
                const data = await response.json();
                
                console.log('Weather data received:', data); // Debug log
                
                if (data.cod === 200) {
                    // Hide the initial message
                    document.getElementById('weatherContent').style.display = 'none';
                    
                    // Display weather info
                    const temp = Math.round(data.main.temp - 273.15); // Convert Kelvin to Celsius
                    const feelsLike = Math.round(data.main.feels_like - 273.15);
                    
                    document.getElementById('weatherMain').textContent = data.weather[0].main;
                    document.getElementById('weatherDesc').textContent = data.weather[0].description;
                    document.getElementById('temperature').textContent = `${temp}°C`;
                    document.getElementById('feelsLike').textContent = `${feelsLike}°C`;
                    document.getElementById('humidity').textContent = `${data.main.humidity}%`;
                    document.getElementById('windSpeed').textContent = `${data.wind.speed} m/s`;
                    document.getElementById('windDirection').textContent = data.wind.deg || 'N/A';
                    
                    // Set weather icon
                    const weatherIcons = {
                        'Clear': '☀️',
                        'Clouds': '☁️',
                        'Rain': '🌧️',
                        'Drizzle': '🌦️',
                        'Thunderstorm': '⛈️',
                        'Snow': '❄️',
                        'Mist': '🌫️',
                        'Fog': '🌫️'
                    };
                    document.getElementById('weatherIcon').textContent = weatherIcons[data.weather[0].main] || '🌤️';
                    
                    // Show weather cards
                    document.getElementById('weatherCards').style.display = 'grid';
                    
                } else {
                    showError('Failed to get weather information: ' + (data.message || 'Unknown error'));
                }
            } catch (error) {
                console.error('Weather error:', error);
                showError('Error getting weather: ' + error.message);
            }
            hideLoading();
        }
        
        async function getWeatherForecast() {
            if (!currentLat || !currentLon) {
                showError('Please get your location first');
                return;
            }
            
            showLoading();
            try {
                const response = await fetch(`/get-forecast?lat=${currentLat}&lon=${currentLon}`);
                const data = await response.json();
                
                console.log('Forecast data received:', data); // Debug log
                
                if (data.cod === "200") {
                    // Hide the initial message
                    document.getElementById('forecastContent').style.display = 'none';
                    
                    // Show the forecast container
                    document.getElementById('forecastResult').style.display = 'block';
                    
                    // Process forecast data
                    const forecastDays = document.getElementById('forecastDays');
                    forecastDays.innerHTML = '';
                    
                    // Group forecasts by day
                    const dailyForecasts = {};
                    const today = new Date().toDateString();
                    
                    data.list.forEach(forecast => {
                        const date = new Date(forecast.dt * 1000);
                        const dayKey = date.toDateString();
                        
                        // Skip today's forecasts
                        if (dayKey === today) return;
                        
                        if (!dailyForecasts[dayKey]) {
                            dailyForecasts[dayKey] = {
                                date: date,
                                temps: [],
                                weather: [],
                                count: 0
                            };
                        }
                        
                        const temp = Math.round(forecast.main.temp - 273.15);
                        dailyForecasts[dayKey].temps.push(temp);
                        dailyForecasts[dayKey].weather.push(forecast.weather[0]);
                        dailyForecasts[dayKey].count++;
                    });
                    
                    // Create forecast cards for each day
                    for (const dayKey in dailyForecasts) {
                        if (Object.keys(dailyForecasts).length > 5) break; // Limit to 5 days
                        
                        const day = dailyForecasts[dayKey];
                        const avgTemp = Math.round(day.temps.reduce((a, b) => a + b, 0) / day.temps.length);
                        const minTemp = Math.min(...day.temps);
                        const maxTemp = Math.max(...day.temps);
                        
                        // Find the most common weather condition
                        const weatherCounts = {};
                        day.weather.forEach(w => {
                            const key = w.main;
                            weatherCounts[key] = (weatherCounts[key] || 0) + 1;
                        });
                        const mostCommonWeather = Object.entries(weatherCounts).reduce((a, b) => 
                            a[1] > b[1] ? a : b)[0];
                        const weatherDesc = day.weather.find(w => w.main === mostCommonWeather).description;
                        
                        // Weather icons
                        const weatherIcons = {
                            'Clear': '☀️',
                            'Clouds': '☁️',
                            'Rain': '🌧️',
                            'Drizzle': '🌦️',
                            'Thunderstorm': '⛈️',
                            'Snow': '❄️',
                            'Mist': '🌫️',
                            'Fog': '🌫️'
                        };
                        
                        // Format date
                        const options = { weekday: 'short', month: 'short', day: 'numeric' };
                        const formattedDate = day.date.toLocaleDateString(undefined, options);
                        
                        // Create forecast card
                        const forecastCard = document.createElement('div');
                        forecastCard.className = 'forecast-day';
                        forecastCard.innerHTML = `
                            <div class="forecast-date">${formattedDate}</div>
                            <div class="weather-icon">${weatherIcons[mostCommonWeather] || '🌤️'}</div>
                            <div class="forecast-temp">${avgTemp}°C</div>
                            <div class="forecast-temp">H: ${maxTemp}°C / L: ${minTemp}°C</div>
                            <div class="forecast-description">${weatherDesc}</div>
                        `;
                        
                        forecastDays.appendChild(forecastCard);
                    }
                    
                } else {
                    showError('Failed to get forecast information: ' + (data.message || 'Unknown error'));
                }
            } catch (error) {
                console.error('Forecast error:', error);
                showError('Error getting forecast: ' + error.message);
            }
            hideLoading();
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

@app.get("/get-location")
async def get_location(request: Request):
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
            
        # Add debug info
        data["debug_ip"] = client_ip
        data["debug_url"] = url
        
        return data
    except Exception as e:
        return {"status": "fail", "message": str(e), "debug": "Exception in get_location"}

@app.get("/get-weather")
async def get_weather(lat: float, lon: float):
    try:
        api_key = "26ca4d17ab7073188de43040d3cbaf93"
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
        return data
    except Exception as e:
        return {"cod": 400, "message": str(e)}

@app.get("/get-forecast")
async def get_forecast(lat: float, lon: float):
    try:
        api_key = "26ca4d17ab7073188de43040d3cbaf93"
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
        return data
    except Exception as e:
        return {"cod": 400, "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)