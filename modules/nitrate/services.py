import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import random

import google.generativeai as genai
import os

from modules.nitrate.schemas import NitrateStatusResponse, NitrateAlert
from modules.sensor_data.services import get_simulated_sensor_data

# Configure your API key
API_KEY = "AIzaSyDBxs1alLA5dJK6n2B6rXHuPoIgfuq0PLk"
if not API_KEY:
    print("WARNING: GOOGLE_API_KEY environment variable not set. Using a placeholder.")
    genai.configure(api_key="placeholder")
else:
    genai.configure(api_key=API_KEY)


# A simple helper function to get the Gemini model instance
def get_gemini_model_for_text():
    """
    Returns a configured Gemini model for text-only generation.
    """
    return genai.GenerativeModel("gemini-1.5-flash-latest")


text_model = get_gemini_model_for_text()


# --- Mock Service for Farm History (simulating a database query) ---
def get_simulated_farm_history(farm_id: Optional[int]) -> Dict[str, Any]:
    """
    Simulates fetching recent farm history, including fertilizer applications.
    In a real system, this would query a database.
    """
    # Create some mock historical data for demonstration
    fertilizer_history = [
        {
            "fertilizer_type": "Urea",
            "quantity_kg_per_acre": 50,
            "application_date": (datetime.now() - timedelta(days=7)).isoformat()
        },
        {
            "fertilizer_type": "D-Compound",
            "quantity_kg_per_acre": 100,
            "application_date": (datetime.now() - timedelta(days=14)).isoformat()
        }
    ]
    return {
        "farm_id": farm_id,
        "fertilizer_history": fertilizer_history
    }


# --- Main Service for Nitrate Monitoring ---
async def get_nitrate_status_from_gemini(
        latitude: float,
        longitude: float,
        farm_id: Optional[int] = None
) -> NitrateStatusResponse:
    """
    Simulates nitrate levels and generates a status report using the Gemini API.
    """
    # Step 1: Simulate/fetch all required data
    sensor_data = get_simulated_sensor_data(latitude, longitude)
    farm_history = get_simulated_farm_history(farm_id)

    # Step 2: Construct a comprehensive prompt
    prompt = f"""
    You are an expert soil scientist and environmental consultant for farms in Zambia.
    Your task is to analyze a farm's conditions and predict the current nitrate leaching risk.

    Conditions:
    - Location: Latitude {latitude}, Longitude {longitude}
    - Soil pH: {sensor_data.soil_ph}
    - Soil Moisture: {sensor_data.soil_moisture}%
    - Electrical Conductivity: {sensor_data.electrical_conductivity} dS/m
    - Recent Fertilizer Applications (last 14 days): {json.dumps(farm_history['fertilizer_history'])}

    Based on this data, simulate the current nitrate level in the soil in parts per million (ppm). Then, assess the risk of nitrate leaching as "Low", "Medium", or "High" and provide a detailed message explaining your assessment. Also, provide any actionable advice to the farmer.

    The response must be in a JSON format. Do not include any text before or after the JSON object.

    Example JSON structure:
    {{
      "current_nitrate_level_ppm": 25.5,
      "alert": {{
        "risk_level": "Medium",
        "message": "Nitrate levels are slightly elevated. This is likely due to the recent fertilizer application combined with high soil moisture. Consider reducing the next fertilizer application to prevent leaching."
      }},
      "notes": "The current soil conditions suggest a moderate risk of nitrogen runoff, which could be harmful to local water sources."
    }}
    """

    print("Sending nitrate monitoring prompt to Gemini API...")
    try:
        response = await text_model.generate_content_async(prompt)
        response_text = response.text
        print(f"Gemini raw response: {response_text}")

        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start != -1 and json_end != -1:
            json_response_string = response_text[json_start:json_end]
            parsed_response = json.loads(json_response_string)

            alert = NitrateAlert(
                risk_level=parsed_response['alert']['risk_level'],
                message=parsed_response['alert']['message']
            )

            return NitrateStatusResponse(
                current_nitrate_level_ppm=parsed_response['current_nitrate_level_ppm'],
                timestamp=datetime.now(),
                alert=alert,
                notes=parsed_response['notes']
            )
        else:
            print("Gemini response did not contain a valid JSON object.")
            return NitrateStatusResponse(
                current_nitrate_level_ppm=0.0,
                timestamp=datetime.now(),
                alert=NitrateAlert(risk_level="Error", message="Could not parse API response."),
                notes="An issue occurred with the recommendation service."
            )

    except Exception as e:
        print(f"Error calling Gemini API for nitrate monitoring: {e}")
        return NitrateStatusResponse(
            current_nitrate_level_ppm=0.0,
            timestamp=datetime.now(),
            alert=NitrateAlert(risk_level="Error", message=f"An issue occurred with the recommendation service: {e}"),
            notes="An error occurred with the nitrate monitoring service."
        )