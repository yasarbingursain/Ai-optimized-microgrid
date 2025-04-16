import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# from app.db import get_db, User, System, PowerQuality, GridStability, LoadBalancing
# from app.config import settings
# from models.predictor import EnergyPredictor

# Dummy fallback settings for local testing
class DummySettings:
    MODEL_PATH = "models/baseline_model.pkl"
    WEATHER_API_KEY = "demo"
    SECRET_KEY = "super-secret-key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    API_HOST = "127.0.0.1"
    API_PORT = 8000
    INFLUXDB_URL = "http://localhost:8086"
    INFLUXDB_TOKEN = "fake-token"
    INFLUXDB_ORG = "demo"
    INFLUXDB_BUCKET = "energy"
    DEFAULT_LATITUDE = 0.0
    DEFAULT_LONGITUDE = 0.0

settings = DummySettings()

app = FastAPI(title="Microgrid Energy Forecasting API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Placeholder predictor logic
class EnergyPredictor:
    def __init__(self, model_path, weather_api_key):
        self.model_path = model_path
        self.weather_api_key = weather_api_key

    def load_model(self):
        print("[INFO] Dummy model loaded from:", self.model_path)

    def predict(self, lat, lon):
        return [{"hour": i, "value": 100 + i} for i in range(24)]

predictor = EnergyPredictor(settings.MODEL_PATH, settings.WEATHER_API_KEY)

# Dummy InfluxDB client setup for testing (optional usage)
influx_client = InfluxDBClient(
    url=settings.INFLUXDB_URL,
    token=settings.INFLUXDB_TOKEN,
    org=settings.INFLUXDB_ORG
)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)
query_api = influx_client.query_api()

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str
    is_active: bool = True
    is_admin: bool = False

@app.on_event("startup")
async def startup_event():
    try:
        predictor.load_model()
    except FileNotFoundError:
        print("Warning: Model not found. Please train the model first.")

@app.get("/forecast")
async def get_forecast(
    lat: float = settings.DEFAULT_LATITUDE,
    lon: float = settings.DEFAULT_LONGITUDE
):
    try:
        forecast = predictor.predict(lat=lat, lon=lon)
        return {"forecast": forecast}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    try:
        query = f'''
        from(bucket: "{settings.INFLUXDB_BUCKET}")
            |> range(start: -1h)
            |> last()
        '''
        result = query_api.query(query=query)
        metrics = {}
        for table in result:
            for record in table.records:
                metrics[record.get_field()] = record.get_value()
        return {"metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
