import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime


async def get_current_weather_and_forecast(
        latitude: float,
        longitude: float,
        num_days: int = 7
) -> Optional[Dict[str, Any]]:
    """
    Fetches a daily weather forecast from the Open-Meteo API.
    No API key is required.
    """
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
        "timezone": "auto",
        "forecast_days": num_days
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(base_url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            processed_forecast = []
            if 'daily' in data and 'time' in data['daily']:
                for i, date_str in enumerate(data['daily']['time']):
                    processed_forecast.append({
                        "date": date_str,
                        "temp_min": data['daily']['temperature_2m_min'][i],
                        "temp_max": data['daily']['temperature_2m_max'][i],
                        "precipitation_sum_mm": data['daily']['precipitation_sum'][i],
                        "precipitation_probability": data['daily']['precipitation_probability_max'][i],
                        "wind_speed_max_kmh": data['daily']['wind_speed_10m_max'][i]
                    })

            return {"daily_forecast": processed_forecast}

        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching Open-Meteo data: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"Request error fetching Open-Meteo data: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred with Open-Meteo API: {e}")
            return None