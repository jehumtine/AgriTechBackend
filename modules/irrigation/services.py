import json
from typing import List, Optional
from datetime import datetime, date, timedelta

import google.generativeai as genai
import os

from modules.irrigation.schemas import IrrigationRecommendation, IrrigationScheduleRequest
from modules.sensor_data.services import get_simulated_sensor_data
from services.open_meteo_client import get_current_weather_and_forecast

# Configure Gemini API
API_KEY = "AIzaSyDBxs1alLA5dJK6n2B6rXHuPoIgfuq0PLk"
if not API_KEY:
    print("WARNING: GOOGLE_API_KEY environment variable not set. Using a placeholder.")
    genai.configure(api_key="placeholder")
else:
    genai.configure(api_key=API_KEY)

text_model = genai.GenerativeModel("gemini-1.5-flash-latest")


# This is a placeholder for future IoT integration
async def send_irrigation_command(
        farm_id: Optional[int],
        duration_minutes: float,
        water_amount_mm: float,
        scheduled_date: date
):
    """
    Simulates sending a command to an IoT device (pump/valve).
    In a real system, this would interact with actual hardware via MQTT, HTTP, etc.
    """
    print(f"\n--- SIMULATING HARDWARE COMMAND ---")
    print(f"Farm ID: {farm_id if farm_id else 'N/A'}")
    print(f"Command: Initiate irrigation for {duration_minutes:.2f} minutes")
    print(f"Estimated water delivery: {water_amount_mm:.2f} mm")
    print(f"Scheduled for: {scheduled_date}")
    print(f"--- COMMAND SIMULATED ---")
    # No actual action taken in simulation
    pass


async def get_irrigation_schedule_from_gemini(
        request_data: IrrigationScheduleRequest
) -> List[IrrigationRecommendation]:
    """
    Generates an irrigation schedule using the Gemini API based on farm conditions,
    sensor data, and weather forecasts.
    """
    # 1. Gather all necessary input data
    sensor_data = get_simulated_sensor_data(request_data.latitude, request_data.longitude)
    weather_data = await get_current_weather_and_forecast(request_data.latitude, request_data.longitude)

    if not weather_data:
        # Handle the case where weather data could not be fetched
        return [
            IrrigationRecommendation(
                next_irrigation_date=date.today(),
                duration_minutes=0.0,
                water_amount_mm=0.0,
                reasoning="Could not fetch weather data. Please try again later."
            )
        ]

    # 2. Construct a comprehensive prompt for Gemini
    prompt = f"""
    You are an expert agricultural engineer specializing in irrigation management for small-scale farms in Zambia.
    Your task is to provide an optimal irrigation schedule for the next 7 days for the specified crop,
    considering the current conditions, real-time sensor data, and weather forecasts.

    Conditions:
    - Crop: {request_data.crop_name}
    - Soil Type: {request_data.soil_type}
    - Location: Latitude {request_data.latitude}, Longitude {request_data.longitude}

    Real-Time Sensor Readings:
    - Soil Moisture: {sensor_data.soil_moisture}%
    - Soil Temperature: {sensor_data.soil_temperature}°C
    - Electrical Conductivity (Salinity): {sensor_data.electrical_conductivity} dS/m
    - Soil pH: {sensor_data.soil_ph}
    - Relative Humidity: {sensor_data.relative_humidity}%
    - Solar Radiation: {sensor_data.solar_radiation} W/m^2

    Weather Forecast for the Next 7 Days:
    {json.dumps(weather_data, indent=2)}

    Based on this information, recommend specific irrigation events. For each event, specify:
    1. The 'next_irrigation_date' (in YYYY-MM-DD format).
    2. The 'duration_minutes' (how long to irrigate in minutes).
    3. The 'water_amount_mm' (estimated water delivered in millimeters).
    4. A 'reasoning' explaining why this schedule is recommended, referencing the provided data points.

    Provide up to 3-5 irrigation events for the upcoming week.
    The response must be a JSON object with a single key 'schedule' containing a list of these recommendations.
    Do not include any text before or after the JSON object.

    Example JSON structure:
    {{
      "schedule": [
        {{
          "next_irrigation_date": "{date.today().isoformat()}",
          "duration_minutes": 30.0,
          "water_amount_mm": 15.0,
          "reasoning": "Current soil moisture is low ({sensor_data.soil_moisture}%) and no significant rain is expected for the next 2 days based on the forecast."
        }},
        {{
          "next_irrigation_date": "{(date.today() + timedelta(days=3)).isoformat()}",
          "duration_minutes": 20.0,
          "water_amount_mm": 10.0,
          "reasoning": "Follow-up irrigation needed due to anticipated dry conditions and {request_data.crop_name}'s water requirements, despite a slight chance of rain on day 2."
        }}
      ]
    }}
    """

    print("Sending detailed irrigation schedule prompt to Gemini API...")
    try:
        response = await text_model.generate_content_async(prompt)
        response_text = response.text
        print(f"Gemini raw response: {response_text}")

        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start != -1 and json_end != -1:
            json_response_string = response_text[json_start:json_end]
            parsed_response = json.loads(json_response_string)

            schedule_list = []
            for rec in parsed_response.get('schedule', []):
                schedule_list.append(
                    IrrigationRecommendation(
                        next_irrigation_date=date.fromisoformat(rec['next_irrigation_date']),
                        duration_minutes=float(rec['duration_minutes']),
                        water_amount_mm=float(rec['water_amount_mm']),
                        reasoning=rec['reasoning']
                    )
                )
            return schedule_list
        else:
            print("Gemini response did not contain a valid JSON object.")
            return [
                IrrigationRecommendation(
                    next_irrigation_date=date.today(),
                    duration_minutes=0.0,
                    water_amount_mm=0.0,
                    reasoning="Could not parse API response for scheduling."
                )
            ]

    except Exception as e:
        print(f"Error calling Gemini API for irrigation scheduling: {e}")
        return [
            IrrigationRecommendation(
                next_irrigation_date=date.today(),
                duration_minutes=0.0,
                water_amount_mm=0.0,
                reasoning=f"An issue occurred with the scheduling service: {e}"
            )
        ]