from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/microgrid")
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")  # Change this in production
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # PostgreSQL Configuration
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "microgrid")
    
    # InfluxDB Configuration
    INFLUXDB_URL: str = os.getenv("INFLUXDB_URL", "http://localhost:8086")
    INFLUXDB_TOKEN: str = os.getenv("INFLUXDB_TOKEN", "your-token-here")
    INFLUXDB_ORG: str = os.getenv("INFLUXDB_ORG", "microgrid")
    INFLUXDB_BUCKET: str = os.getenv("INFLUXDB_BUCKET", "energy_metrics")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Model Configuration
    MODEL_PATH: str = os.getenv("MODEL_PATH", "models/")
    
    # Weather API Configuration
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")
    DEFAULT_LATITUDE: float = float(os.getenv("DEFAULT_LATITUDE", "0.0"))
    DEFAULT_LONGITUDE: float = float(os.getenv("DEFAULT_LONGITUDE", "0.0"))
    
    # Additional Metrics
    ENABLE_POWER_QUALITY: bool = os.getenv("ENABLE_POWER_QUALITY", "true").lower() == "true"
    ENABLE_GRID_STABILITY: bool = os.getenv("ENABLE_GRID_STABILITY", "true").lower() == "true"
    ENABLE_LOAD_BALANCING: bool = os.getenv("ENABLE_LOAD_BALANCING", "true").lower() == "true"
    
    class Config:
        env_file = ".env"

settings = Settings() 