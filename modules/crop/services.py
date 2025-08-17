# app/modules/crop/services.py
import os
import json
import google.generativeai as genai
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from modules.crop.schemas import RecommendationRequest, CropRecommendation
from modules.crop.model import CropRecommendation as CropRecommendationModel  # Renamed to avoid clash
from modules.sensor_data.services import get_simulated_sensor_data
from core.config import settings

# Configure Gemini API
API_KEY = "AIzaSyDBxs1alLA5dJK6n2B6rXHuPoIgfuq0PLk"
if not API_KEY:
    print("WARNING: GOOGLE_API_KEY environment variable not set. Using a placeholder.")
    genai.configure(api_key="placeholder")
else:
    genai.configure(api_key=API_KEY)

text_model = genai.GenerativeModel("gemini-1.5-flash-latest")


async def get_crop_recommendations_from_gemini(
        request_data: RecommendationRequest,
        db: Session
) -> List[CropRecommendation]:
    """
    Generates a list of crop recommendations based on location data, saves them
    to the database, and returns the parsed list.
    """
    # 1. Gather all necessary input data
    sensor_data = get_simulated_sensor_data(request_data.latitude, request_data.longitude)

    # 2. Construct a prompt for Gemini
    prompt = f"""
    You are an expert agronomist for small-scale farming in Zambia.
    Your task is to provide a list of top 3 optimal crop recommendations for a farm based on its soil type and current sensor data.
    For each recommendation, provide a detailed reasoning and a suitability score from 0 to 1.

    Conditions:
    - Soil Type: {request_data.soil_type}
    - Location: Latitude {request_data.latitude}, Longitude {request_data.longitude}

    Real-Time Sensor Readings:
    - Soil Moisture: {sensor_data.soil_moisture}%
    - Soil Temperature: {sensor_data.soil_temperature}°C
    - Electrical Conductivity (Salinity): {sensor_data.electrical_conductivity} dS/m
    - Soil pH: {sensor_data.soil_ph}
    - Relative Humidity: {sensor_data.relative_humidity}%
    - Solar Radiation: {sensor_data.solar_radiation} W/m^2
    - Nitrate Level: {sensor_data.nitrate_ppm} ppm

    The response must be a JSON object with a single key 'recommendations' that contains a list of 3 objects, each with 'crop_name', 'reasoning', and 'suitability_score'. Do not include any text before or after the JSON.

    Example JSON structure:
    {{
      "recommendations": [
        {{
          "crop_name": "Maize",
          "reasoning": "Maize is highly suitable for the current loamy sand soil and is a staple crop in Zambia. The sensor data indicates optimal moisture and pH levels for its growth.",
          "suitability_score": 0.95
        }},
        {{
          "crop_name": "Sorghum",
          "reasoning": "Sorghum is a drought-resistant crop, making it a good secondary option. It can tolerate the high solar radiation and is less sensitive to variations in soil moisture.",
          "suitability_score": 0.88
        }}
      ]
    }}
    """

    print("Sending crop recommendation prompt to Gemini API...")
    try:
        response = await text_model.generate_content_async(prompt)
        response_text = response.text

        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start != -1 and json_end != -1:
            json_response_string = response_text[json_start:json_end]
            parsed_response = json.loads(json_response_string)
            recommendations_list = parsed_response.get("recommendations", [])

            # Save each recommendation to the database
            for rec in recommendations_list:
                new_recommendation = CropRecommendationModel(
                    farm_id=request_data.farm_id,
                    soil_type=request_data.soil_type,
                    latitude=request_data.latitude,
                    longitude=request_data.longitude,
                    soil_moisture=sensor_data.soil_moisture,
                    soil_temperature=sensor_data.soil_temperature,
                    electrical_conductivity=sensor_data.electrical_conductivity,
                    soil_ph=sensor_data.soil_ph,
                    relative_humidity=sensor_data.relative_humidity,
                    solar_radiation=sensor_data.solar_radiation,
                    nitrate_ppm=sensor_data.nitrate_ppm,
                    recommended_crop=rec['crop_name'],
                    reasoning=rec['reasoning']
                )
                db.add(new_recommendation)

            db.commit()

            # Return the parsed list of Pydantic models
            return [
                CropRecommendation(
                    crop_name=rec['crop_name'],
                    reasoning=rec['reasoning'],
                    suitability_score=rec['suitability_score']
                ) for rec in recommendations_list
            ]
        else:
            print("Gemini response did not contain a valid JSON object.")
            db.rollback()
            return []
    except Exception as e:
        print(f"Error calling Gemini API for crop recommendation: {e}")
        db.rollback()
        return []