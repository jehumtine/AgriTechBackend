from typing import List
import json
from datetime import datetime

from services.gemini_ai_client import get_gemini_model_for_text
from modules.crop.schemas import CropRecommendation

# We will need a specific model for this task, so we create a new one.
text_model = get_gemini_model_for_text()


async def get_crop_recommendations_from_gemini(
        soil_type: str,
        season: str,
        zone: str,
        latitude: float,
        longitude: float,
        soil_moisture: float,
        soil_temperature: float,
        electrical_conductivity: float,
        soil_ph: float,
        relative_humidity: float,
        solar_radiation: float,
) -> List[CropRecommendation]:
    """
    Generates crop recommendations using the Gemini API based on detailed user inputs
    and sensor data.
    """
    # Construct a detailed prompt for the Gemini API
    prompt = f"""
    You are an expert agricultural advisor for farmers in Zambia.
    Based on the following conditions, recommend 3 to 5 crops that are most suitable for cultivation.

    Conditions:
    - **General Farm Details:**
        - Soil Type: {soil_type}
        - Current Season: {season}
        - Agro-ecological Zone: {zone}
        - Latitude: {latitude}
        - Longitude: {longitude}
    - **Real-Time Sensor Readings:**
        - Soil Moisture: {soil_moisture}%
        - Soil Temperature: {soil_temperature}°C
        - Electrical Conductivity (Salinity): {electrical_conductivity} dS/m
        - Soil pH: {soil_ph}
        - Relative Humidity: {relative_humidity}%
        - Solar Radiation: {solar_radiation} W/m^2

    For each recommended crop, provide a brief, clear explanation (reasoning) of why it is suitable under these specific conditions. Also, provide a 'suitability_score' from 0.0 to 1.0 (where 1.0 is a perfect match) for each crop, based on how well it fits the criteria.
    The response must be in a JSON format. Do not include any text before or after the JSON object.

    Example JSON structure:
    {{
      "recommendations": [
        {{
          "crop_name": "Maize",
          "reasoning": "Maize is well-suited for loamy soils and is drought-resistant, making it a good choice for the dry season. The current soil moisture and temperature are within its optimal range.",
          "suitability_score": 0.95
        }},
        {{
          "crop_name": "Sorghum",
          "reasoning": "Sorghum thrives in hot and dry conditions and can handle various soil types, making it a robust alternative for this zone. It is particularly tolerant of the current electrical conductivity levels.",
          "suitability_score": 0.88
        }}
      ]
    }}
    """

    print("Sending detailed prompt to Gemini API...")
    try:
        response = await text_model.generate_content_async(prompt)
        response_text = response.text
        print(f"Gemini raw response: {response_text}")

        # The API might sometimes add extra characters, so we try to find the JSON part.
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start != -1 and json_end != -1:
            json_response_string = response_text[json_start:json_end]
            parsed_response = json.loads(json_response_string)

            recommendations_list = [
                CropRecommendation(
                    crop_name=rec['crop_name'],
                    reasoning=rec['reasoning'],
                    suitability_score=rec['suitability_score']
                ) for rec in parsed_response['recommendations']
            ]
            return recommendations_list
        else:
            print("Gemini response did not contain a valid JSON object.")
            return [
                CropRecommendation(crop_name="Error", reasoning="Could not parse API response.", suitability_score=0.0)]

    except Exception as e:
        print(f"Error calling Gemini API for crop recommendation: {e}")
        return [CropRecommendation(crop_name="Error", reasoning="An issue occurred with the recommendation service.",
                                   suitability_score=0.0)]