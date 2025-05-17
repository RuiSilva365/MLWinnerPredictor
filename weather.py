# weather.py
# Module for fetching and caching weather data from Open-Meteo API
import pandas as pd
import requests
import logging
from datetime import datetime, timedelta
import json
import os
from typing import Dict, Optional
import url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('weather.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Cache file for weather data
WEATHER_CACHE_FILE = "weather_cache.json"

def load_weather_cache() -> Dict:
    """Load weather cache from file."""
    if os.path.exists(WEATHER_CACHE_FILE):
        try:
            with open(WEATHER_CACHE_FILE, 'r') as f:
                cache = json.load(f)
                logger.info(f"Loaded {len(cache)} valid cache entries")
                return cache
        except Exception as e:
            logger.error(f"Error loading weather cache: {str(e)}")
    return {}

def save_weather_cache(cache: Dict) -> None:
    """Save weather cache to file."""
    try:
        with open(WEATHER_CACHE_FILE, 'w') as f:
            json.dump(cache, f)
        logger.info(f"Saved weather cache with {len(cache)} entries")
    except Exception as e:
        logger.error(f"Error saving weather cache: {str(e)}")

def get_weather_data(lat: float, lon: float, date_str: str, time_str: str = "20:00") -> Optional[Dict]:
    """Fetch weather data for a specific date, time, and location."""
    cache = load_weather_cache()
    cache_key = f"{lat}_{lon}_{date_str}_{time_str}"
    
    if cache_key in cache:
        logger.info(f"Cache hit for {cache_key}")
        return cache[cache_key]
    
    try:
        # Parse date
        date_formats = ['%d/%m/%Y', '%Y-%m-%d']
        date_obj = None
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                logger.info(f"Parsed date {date_str} with format {fmt}")
                break
            except ValueError:
                continue
        if not date_obj:
            raise ValueError(f"Invalid date format: {date_str}")
        
        # Check if date is in the future
        current_date = datetime.now()
        is_future = date_obj.date() > current_date.date()
        forecast_window = (current_date + timedelta(days=16)).date()
        
        # Determine API and date to use
        if is_future and date_obj.date() <= forecast_window:
            # Use forecast API for future dates within 16 days
            base_url = 'https://api.open-meteo.com/v1/forecast'
            api_date = date_obj
            logger.info(f"Using forecast API for {date_str}")
        else:
            # Use archive API with historical proxy
            base_url = 'https://archive-api.open-meteo.com/v1/archive'
            api_date = date_obj.replace(year=current_date.year - 1) if is_future else date_obj
            logger.info(f"Using archive API with proxy date {api_date.strftime('%Y-%m-%d')} for {date_str}")
        
        # Construct API URL
        start_date = api_date.strftime('%Y-%m-%d')
        end_date = (api_date + timedelta(days=1)).strftime('%Y-%m-%d')
        api_url = (
            f"{base_url}?"
            f"latitude={lat}&longitude={lon}&"
            f"start_date={start_date}&end_date={end_date}&"
            f"hourly=temperature_2m,precipitation,weathercode"
        )
        
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Find closest hourly data
        target_time = datetime.strptime(f"{api_date.strftime('%Y-%m-%d')} {time_str}", '%Y-%m-%d %H:%M')
        hourly_data = data.get('hourly', {})
        times = hourly_data.get('time', [])
        
        closest_idx = None
        min_diff = float('inf')
        for idx, time_str_api in enumerate(times):
            time_obj = datetime.strptime(time_str_api, '%Y-%m-%dT%H:%M')
            diff = abs((time_obj - target_time).total_seconds())
            if diff < min_diff:
                min_diff = diff
                closest_idx = idx
        
        if closest_idx is None:
            raise ValueError("No hourly weather data available")
        
        # Extract weather data
        weather_data = {
            'Temperature': hourly_data['temperature_2m'][closest_idx],
            'Precipitation': hourly_data['precipitation'][closest_idx],
            'WeatherCode': hourly_data['weathercode'][closest_idx],
            'Weather': map_weather_code(hourly_data['weathercode'][closest_idx])
        }
        
        # Cache the result
        cache[cache_key] = weather_data
        save_weather_cache(cache)
        
        logger.info(f"Fetched weather for {date_str} {time_str} at ({lat}, {lon}): {weather_data}")
        return weather_data
    
    except Exception as e:
        logger.error(f"Error fetching weather for {date_str} {time_str} at ({lat}, {lon}): {str(e)}")
        # Return default weather data
        default_weather = {
            'Temperature': 15.0,
            'Precipitation': 0.0,
            'WeatherCode': 0,
            'Weather': 'Clear'
        }
        logger.warning(f"Using default weather data: {default_weather}")
        cache[cache_key] = default_weather
        save_weather_cache(cache)
        return default_weather

def map_weather_code(code: int) -> str:
    """Map Open-Meteo weather code to human-readable description."""
    weather_codes = {
        0: "Clear",
        1: "Mostly Clear",
        2: "Partly Cloudy",
        3: "Cloudy",
        45: "Fog",
        48: "Fog",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Dense Drizzle",
        61: "Light Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        71: "Light Snow",
        73: "Moderate Snow",
        75: "Heavy Snow",
        95: "Thunderstorm"
    }
    return weather_codes.get(code, "Unknown")

def enrich_with_weather(df: pd.DataFrame, league: str) -> pd.DataFrame:
    """Enrich DataFrame with weather data for each match."""
    if df.empty:
        logger.warning("Input DataFrame is empty")
        return df
    
    result_df = df.copy()
    result_df['Temperature'] = None
    result_df['Precipitation'] = None
    result_df['WeatherCode'] = None
    result_df['Weather'] = 'Unknown'
    
    for idx, row in result_df.iterrows():
        home_team = row['HomeTeam']
        date_str = row['Date']
        time_str = row.get('Time', '20:00')
        
        if pd.isna(date_str) or not home_team:
            logger.warning(f"Missing Date or HomeTeam at index {idx}")
            continue
        
        # Get coordinates
        coords = url.club_to_city.get(home_team)
        if not coords:
            logger.warning(f"No coordinates found for {home_team}")
            continue
        
        # Fetch weather
        logger.info(f"Fetching weather for {date_str} {time_str} at ({coords['lat']}, {coords['lon']})")
        weather_data = get_weather_data(coords['lat'], coords['lon'], date_str, time_str)
        
        if weather_data:
            result_df.at[idx, 'Temperature'] = weather_data['Temperature']
            result_df.at[idx, 'Precipitation'] = weather_data['Precipitation']
            result_df.at[idx, 'WeatherCode'] = weather_data['WeatherCode']
            result_df.at[idx, 'Weather'] = weather_data['Weather']
            logger.info(f"Applied weather data for {home_team} on {date_str}: {weather_data}")
    
    logger.info(f"Enriched DataFrame with weather data: {len(result_df)} rows")
    return result_df