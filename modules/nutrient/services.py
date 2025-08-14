# app/modules/nutrient/services.py
import json
from typing import List
from datetime import datetime

import google.generativeai as genai
import os

from modules.nutrient.schemas import FertilizerRecommendation, InternalNutrientPlanRequest

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

async def get_nutrient_plan_from_gemini(
    request_data: InternalNutrientPlanRequest
) -> List[FertilizerRecommendation]:
    """
    Generates a detailed nutrient plan using the Gemini API based on a full request schema,
    including real-time sensor data.
    """
    prompt = f"""
    You are an expert agricultural consultant specializing in soil and nutrient management for farmers in Zambia.
    Based on the following farm conditions and real-time sensor data, create a detailed nutrient plan for the specified crop.

    Conditions:
    - Crop: {request_data.crop_name}
    - Soil Type: {request_data.soil_type}
    - Current Season: {request_data.season}
    - Agro-ecological Zone: {request_data.zone}
    - Location: Latitude {request_data.latitude}, Longitude {request_data.longitude}

    Real-Time Sensor Readings:
    - Soil Moisture: {request_data.soil_moisture}%
    - Soil Temperature: {request_data.soil_temperature}°C
    - Electrical Conductivity (Salinity): {request_data.electrical_conductivity} dS/m
    - Soil pH: {request_data.soil_ph}
    - Relative Humidity: {request_data.relative_humidity}%
    - Solar Radiation: {request_data.solar_radiation} W/m^2

    Your response must contain a list of fertilizer recommendations covering different growth stages. Include both synthetic and organic fertilizer options where appropriate. For each recommendation, specify:
    1. The type of fertilizer (e.g., "Urea", "Compost").
    2. The growth stage for application (e.g., "Planting", "Vegetative Stage", "Flowering").
    3. The recommended quantity in kilograms per acre (kg/acre).
    4. Any additional notes or instructions, especially how the recommendation relates to the sensor readings.

    The response must be a JSON object with a single key 'plan_details' containing a list of these recommendations. Do not include any text before or after the JSON object.

    Example JSON structure:
    {{
      "plan_details": [
        {{
          "fertilizer_type": "D-Compound (Synthetic)",
          "application_stage": "Planting",
          "quantity_per_acre_kg": 50.0,
          "notes": "Apply at the time of planting to provide a strong foundation, as the current soil pH is ideal for initial nutrient uptake."
        }},
        {{
          "fertilizer_type": "Compost (Organic)",
          "application_stage": "Vegetative Stage",
          "quantity_per_acre_kg": 200.0,
          "notes": "Top-dress the soil to improve organic matter and water retention, especially given the low soil moisture reading."
        }}
      ]
    }}
    """
    print("Sending detailed nutrient plan prompt to Gemini API...")
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

            plan_details = [
                FertilizerRecommendation(
                    fertilizer_type=rec['fertilizer_type'],
                    application_stage=rec['application_stage'],
                    quantity_per_acre_kg=rec['quantity_per_acre_kg'],
                    notes=rec['notes']
                ) for rec in parsed_response['plan_details']
            ]
            return plan_details
        else:
            print("Gemini response did not contain a valid JSON object.")
            return [
                FertilizerRecommendation(
                    fertilizer_type="Error",
                    application_stage="N/A",
                    quantity_per_acre_kg=0.0,
                    notes="Could not parse API response."
                )
            ]

    except Exception as e:
        print(f"Error calling Gemini API for nutrient plan generation: {e}")
        return [
            FertilizerRecommendation(
                fertilizer_type="Error",
                application_stage="N/A",
                quantity_per_acre_kg=0.0,
                notes=f"An issue occurred with the recommendation service: {e}"
            )
        ]