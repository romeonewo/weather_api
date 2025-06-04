from fastapi.responses import HTMLResponse

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Location & Weather API Demo</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            padding: 40px;
            backdrop-filter: blur(10px);
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        h1 {
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 3em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            color: #718096;
            font-size: 1.2em;
            margin-bottom: 30px;
        }
        
        .api-links {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .api-link {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .api-link:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        }
        
        .button {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 16px;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            margin: 10px;
        }
        
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        .button:disabled {
            background: #cbd5e0;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .info-box {
            background: linear-gradient(135deg, #f7fafc, #edf2f7);
            border: 2px solid #667eea;
            border-radius: 15px;
            padding: 25px;
            margin: 25px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .info-box h3 {
            color: #2d3748;
            margin-top: 0;
            font-size: 1.5em;
        }
        
        .location-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        
        .info-item {
            background: white;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .info-label {
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 5px;
        }
        
        #map {
            height: 400px;
            width: 100%;
            border-radius: 15px;
            margin: 20px 0;
            border: 3px solid #667eea;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .weather-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 25px 0;
        }
        
        .weather-card {
            background: linear-gradient(135deg, #f0f4ff, #e6f3ff);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            border: 2px solid #667eea;
            transition: transform 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .weather-card:hover {
            transform: translateY(-5px);
        }
        
        .weather-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .loading {
            text-align: center;
            color: #667eea;
            font-style: italic;
            font-size: 1.1em;
        }
        
        .error {
            color: #e53e3e;
            background: #fed7d7;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            border-left: 4px solid #e53e3e;
        }
        
        .forecast-container {
            margin-top: 30px;
        }
        
        .forecast-header {
            text-align: center;
            margin-bottom: 25px;
            color: #2d3748;
            font-size: 1.8em;
        }
        
        .forecast-days {
            display: flex;
            overflow-x: auto;
            gap: 20px;
            padding: 15px 0;
        }
        
        .forecast-day {
            min-width: 180px;
            background: linear-gradient(135deg, #f0f4ff, #e6f3ff);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            border: 2px solid #667eea;
            transition: transform 0.3s ease;
        }
        
        .forecast-day:hover {
            transform: scale(1.05);
        }
        
        .forecast-date {
            font-weight: bold;
            margin-bottom: 15px;
            color: #2d3748;
            font-size: 1.1em;
        }
        
        .forecast-temp {
            margin: 8px 0;
            font-weight: 600;
        }
        
        .forecast-description {
            font-size: 0.9em;
            color: #4a5568;
            font-style: italic;
        }
        
        .forecast-days::-webkit-scrollbar {
            height: 10px;
        }
        
        .forecast-days::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        
        .forecast-days::-webkit-scrollbar-thumb {
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 10px;
        }
        
        .forecast-days::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(45deg, #5a67d8, #6b46c1);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌍 Location & Weather API</h1>
            <p class="subtitle">Professional API with Interactive Demo</p>
            <div class="api-links">
                <a href="/docs" class="api-link" target="_blank">📚 API Documentation</a>
                <a href="/redoc" class="api-link" target="_blank">📖 ReDoc</a>
            </div>
        </div>
        
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
                        <div class="info-label">Country</div>
                        <div id="country">Click "Get Current Location" first</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Coordinates</div>
                        <div id="coordinates">Click "Get Current Location" first</div>
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
                <div class="weather-info" id="weatherCards" style="display: none;">
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
                const response = await fetch('/api/location');
                const data = await response.json();
                
                console.log('Location data received:', data);
                
                if (data.status === 'success' || data.lat) {
                    document.getElementById('city').textContent = data.city || 'Unknown';
                    document.getElementById('region').textContent = data.regionName || data.region || 'Unknown';
                    document.getElementById('country').textContent = data.country || 'Unknown';
                    
                    if (data.lat && data.lon) {
                        document.getElementById('coordinates').textContent = `${data.lat.toFixed(6)}, ${data.lon.toFixed(6)}`;
                        currentLat = data.lat;
                        currentLon = data.lon;
                        initMap(data.lat, data.lon, data.city || 'Your Location');
                    }
                } else {
                    showError('Failed to get location information: ' + (data.message || 'Unknown error'));
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
                const response = await fetch(`/api/weather?lat=${currentLat}&lon=${currentLon}`);
                const data = await response.json();
                
                console.log('Weather data received:', data);
                
                if (data.cod === 200) {
                    document.getElementById('weatherContent').style.display = 'none';
                    
                    const temp = Math.round(data.main.temp - 273.15);
                    const feelsLike = Math.round(data.main.feels_like - 273.15);
                    
                    document.getElementById('weatherMain').textContent = data.weather[0].main;
                    document.getElementById('weatherDesc').textContent = data.weather[0].description;
                    document.getElementById('temperature').textContent = `${temp}°C`;
                    document.getElementById('feelsLike').textContent = `${feelsLike}°C`;
                    document.getElementById('humidity').textContent = `${data.main.humidity}%`;
                    document.getElementById('windSpeed').textContent = `${data.wind.speed} m/s`;
                    document.getElementById('windDirection').textContent = data.wind.deg || 'N/A';
                    
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
                const response = await fetch(`/api/forecast?lat=${currentLat}&lon=${currentLon}`);
                const data = await response.json();
                
                console.log('Forecast data received:', data);
                
                if (data.cod === "200") {
                    document.getElementById('forecastContent').style.display = 'none';
                    document.getElementById('forecastResult').style.display = 'block';
                    
                    const forecastDays = document.getElementById('forecastDays');
                    forecastDays.innerHTML = '';
                    
                    const dailyForecasts = {};
                    const today = new Date().toDateString();
                    
                    data.list.forEach(forecast => {
                        const date = new Date(forecast.dt * 1000);
                        const dayKey = date.toDateString();
                        
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
                    
                    let dayCount = 0;
                    for (const dayKey in dailyForecasts) {
                        if (dayCount >= 5) break;
                        
                        const day = dailyForecasts[dayKey];
                        const avgTemp = Math.round(day.temps.reduce((a, b) => a + b, 0) / day.temps.length);
                        const minTemp = Math.min(...day.temps);
                        const maxTemp = Math.max(...day.temps);
                        
                        const weatherCounts = {};
                        day.weather.forEach(w => {
                            const key = w.main;
                            weatherCounts[key] = (weatherCounts[key] || 0) + 1;
                        });
                        const mostCommonWeather = Object.entries(weatherCounts).reduce((a, b) => 
                            a[1] > b[1] ? a : b)[0];
                        const weatherDesc = day.weather.find(w => w.main === mostCommonWeather).description;
                        
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
                        
                        const options = { weekday: 'short', month: 'short', day: 'numeric' };
                        const formattedDate = day.date.toLocaleDateString(undefined, options);
                        
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
                        dayCount++;
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

# Note: I've truncated the actual HTML/CSS content for brevity, 
# but you should include the full template from your original code