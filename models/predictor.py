import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from datetime import datetime, timedelta
import os
import requests
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def get_current_weather(self, lat: float, lon: float) -> Dict:
        """Fetch current weather data from OpenWeatherMap API"""
        try:
            response = requests.get(
                f"{self.base_url}/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric"
                }
            )
            response.raise_for_status()
            data = response.json()
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "cloud_cover": data["clouds"]["all"]
            }
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            return None

class EnergyPredictor:
    def __init__(self, model_path="models/", weather_api_key: Optional[str] = None):
        self.model_path = model_path
        self.models = {
            "random_forest": RandomForestRegressor(n_estimators=200, random_state=42),
            "gradient_boosting": GradientBoostingRegressor(n_estimators=200, random_state=42)
        }
        self.scaler = StandardScaler()
        self.weather_api = WeatherAPI(weather_api_key) if weather_api_key else None
        self.best_model = None
        self.features = None
        
    def train(self, data_path="data/training_data.csv"):
        """Train multiple models and select the best one"""
        # Load and preprocess data
        df = pd.read_csv(data_path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # Feature engineering
        df['hour'] = df['datetime'].dt.hour
        df['day_of_week'] = df['datetime'].dt.dayofweek
        df['month'] = df['datetime'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['season'] = df['datetime'].dt.month % 12 // 3 + 1
        
        # Prepare features and target
        self.features = ['hour', 'day_of_week', 'month', 'is_weekend', 'season',
                        'temperature', 'humidity', 'solar_irradiance', 'wind_speed']
        X = df[self.features]
        y = df['energy_demand']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train and evaluate models
        best_score = float('-inf')
        for name, model in self.models.items():
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            score = r2_score(y_test, y_pred)
            logger.info(f"{name} R2 score: {score:.4f}")
            
            if score > best_score:
                best_score = score
                self.best_model = model
                logger.info(f"New best model: {name}")
        
        # Save best model and scaler
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            'model': self.best_model,
            'scaler': self.scaler,
            'features': self.features
        }, os.path.join(self.model_path, "best_model.pkl"))
        
    def load_model(self):
        """Load trained model from disk"""
        model_file = os.path.join(self.model_path, "best_model.pkl")
        if os.path.exists(model_file):
            saved_data = joblib.load(model_file)
            self.best_model = saved_data['model']
            self.scaler = saved_data['scaler']
            self.features = saved_data['features']
        else:
            raise FileNotFoundError(f"Model not found at {model_file}")
            
    def get_weather_data(self, lat: float, lon: float) -> Dict:
        """Get weather data from API or use default values"""
        if self.weather_api and self.weather_api.api_key:
            weather_data = self.weather_api.get_current_weather(lat, lon)
            if weather_data:
                return weather_data
                
        # Default values if API fails or not configured
        return {
            'temperature': 25.0,
            'humidity': 60.0,
            'wind_speed': 5.0,
            'cloud_cover': 50.0
        }
            
    def predict(self, start_time=None, lat: float = 0.0, lon: float = 0.0) -> List[Dict]:
        """Generate 24-hour forecast with weather data"""
        if start_time is None:
            start_time = datetime.now()
            
        if self.best_model is None:
            self.load_model()
            
        # Get current weather data
        weather_data = self.get_weather_data(lat, lon)
        
        # Generate 24-hour forecast
        forecast_hours = []
        for i in range(24):
            forecast_time = start_time + timedelta(hours=i)
            features = {
                'hour': forecast_time.hour,
                'day_of_week': forecast_time.weekday(),
                'month': forecast_time.month,
                'is_weekend': int(forecast_time.weekday() in [5, 6]),
                'season': forecast_time.month % 12 // 3 + 1,
                'temperature': weather_data['temperature'],
                'humidity': weather_data['humidity'],
                'wind_speed': weather_data['wind_speed'],
                'solar_irradiance': max(0, 1000 * (1 - weather_data['cloud_cover'] / 100))
            }
            forecast_hours.append(features)
            
        # Convert to DataFrame and scale
        forecast_df = pd.DataFrame(forecast_hours)
        X_scaled = self.scaler.transform(forecast_df[self.features])
        
        # Generate predictions
        predictions = self.best_model.predict(X_scaled)
        
        # Format output with additional information
        result = []
        for i, pred in enumerate(predictions):
            forecast_time = start_time + timedelta(hours=i)
            result.append({
                'datetime': forecast_time.isoformat(),
                'predicted_demand': float(pred),
                'weather': {
                    'temperature': weather_data['temperature'],
                    'humidity': weather_data['humidity'],
                    'wind_speed': weather_data['wind_speed'],
                    'solar_irradiance': features['solar_irradiance']
                }
            })
            
        return result 