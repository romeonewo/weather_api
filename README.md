# 🌦️ Weather API & Demo Interface

A modern FastAPI-based project providing IP-based location detection and weather forecasting, with optional HTML demo UI. This project uses:

- **IP-API** for location data  
- **OpenWeatherMap** for weather information

---

## 📁 Project Structure

```plaintext
weather_api/
├── api/                  # Pure API implementation (FastAPI routes + Swagger UI)
│   └── __pycache__/
│
├── app/                  # Full application: API + demo HTML UI
│   └── __pycache__/
│
├── .notebook/            # Notebook output or personal notes
│   └── 20250604/
│
├── demo.py               # Self-contained app (API + demo UI)
├── demo_0.py             # Another version of the self-contained app
├── requirements.txt      # Python dependencies
└── __pycache__/          # Python cache
```

## 📄 Files Overview

### 🔸 `demo.py` & `demo_0.py`
**Standalone files containing everything:**
- FastAPI app
- Weather/location endpoints  
- HTML response demo  

**Use these if you want to run everything from a single file.**

### 🔸 `api/` directory
- Contains only the API endpoints  
- Good for building headless API services  
- Swagger UI included at `/docs`  

### 🔸 `app/` directory
- Mirrors `api/` but adds HTML demo support  
- Best used when you want an interactive interface with your API  

## 🚀 Running the Project

### 🔧 Step 1: Install Dependencies
From your project directory:
```bash
pip install -r requirements.txt
```

## 🚀 Running the Project

### 🔧 Step 1: Install Dependencies
From your project directory:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install fastapi uvicorn httpx
```

### ▶️ Running Options

**Option 1: Run demo.py**  
Self-contained API + demo interface.
```bash
uvicorn demo:app --reload
```

Access:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

**Option 2: Run app/main.py**  
Runs API with demo HTML template (if using modular layout):
```bash
uvicorn app.main:app --reload
```

**Option 3: Run api/main.py**  
API-only (no HTML demo interface):
```bash
uvicorn api.main:app --reload
```

### 📘 API Endpoints

All versions include:
- `GET /api/location` — Location by IP
- `GET /api/weather?lat=...&lon=...` — Current weather by coordinates
- `GET /api/forecast?lat=...&lon=...` — 5-day forecast by coordinates
- `GET /api/weather-by-city?city=...` — Current weather by city
- `GET /api/forecast-by-city?city=...` — 5-day forecast by city
- `GET /api/health` — Health check
- `GET /api/info` — API info

### 📚 Swagger Docs

Once running, explore your API:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc UI:** http://127.0.0.1:8000/redoc