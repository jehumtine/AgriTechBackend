# app/modules/nutrient/services.py
import json
from typing import List
from datetime import datetime

import google.generativeai as genai
import os
from sqlalchemy.orm import Session  # Import Session for database operations

from modules.nutrient.schemas import NutrientPlanRequest, FertilizerRecommendation, NutrientPlanResponse  # Removed InternalNutrientPlanRequest
from modules.nutrient.model import NutrientPlan  # Import the NutrientPlan ORM model
from modules.sensor_data.services import get_simulated_sensor_data  # Re-use sensor data simulator
from core.config import settings  # Assuming settings holds API_KEY

# Configure Gemini API
API_KEY = "AIzaSyDBxs1alLA5dJK6n2B6rXHuPoIgfuq0PLk"
if not API_KEY:
    print("WARNING: GOOGLE_API_KEY environment variable not set. Using a placeholder.")
    genai.configure(api_key="placeholder")
else:
    genai.configure(api_key=API_KEY)

text_model = genai.GenerativeModel("gemini-1.5-flash-latest")


async def get_nutrient_plan_from_gemini(
        request_data: NutrientPlanRequest,
        db: Session  # Database session to save data
) -> List[FertilizerRecommendation]:
    """
    Generates a detailed nutrient plan using the Gemini API based on farm conditions
    and sensor data, saves the full plan to the database, and returns parsed recommendations.
    """
    # 1. Gather all necessary input data, including simulated sensor data
    sensor_data = get_simulated_sensor_data(request_data.latitude, request_data.longitude)

    # 2. Construct a comprehensive prompt for Gemini
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
    - Soil Moisture: {sensor_data.soil_moisture}%
    - Soil Temperature: {sensor_data.soil_temperature}°C
    - Electrical Conductivity (Salinity): {sensor_data.electrical_conductivity} dS/m
    - Soil pH: {sensor_data.soil_ph}
    - Relative Humidity: {sensor_data.relative_humidity}%
    - Solar Radiation: {sensor_data.solar_radiation} W/m^2
    - Nitrate Level: {sensor_data.nitrate_ppm} ppm

    Your response must contain a list of fertilizer recommendations covering different growth stages. Include both synthetic and organic fertilizer options where appropriate. For each recommendation, specify:
    1. The 'fertilizer_type' (e.g., "Urea (Synthetic)", "Compost (Organic)").
    2. The 'application_stage' (e.g., "Planting", "Vegetative Stage", "Flowering").
    3. The 'quantity_per_acre_kg' (recommended quantity in kilograms per acre).
    4. Any additional 'notes' or instructions, especially how the recommendation relates to the sensor readings.

    The response must be a JSON object with a single key 'plan_details' containing a list of these recommendations. Do not include any text before or after the JSON object.

    Example JSON structure:
    {{
      "plan_details": [
        {{
          "fertilizer_type": "D-Compound (Synthetic)",
          "application_stage": "Planting",
          "quantity_per_acre_kg": 50.0,
          "notes": "Apply at planting. Current soil pH ({sensor_data.soil_ph}) is good for phosphorus uptake, supporting root development."
        }},
        {{
          "fertilizer_type": "Compost (Organic)",
          "application_stage": "Vegetative Stage",
          "quantity_per_acre_kg": 200.0,
          "notes": "Top-dress to improve organic matter and moisture retention, vital given current soil moisture ({sensor_data.soil_moisture}%)."
        }}
      ]
    }}
    """

    print("Sending detailed nutrient plan prompt to Gemini API...")
    try:
        response = await text_model.generate_content_async(prompt)
        full_json_response_string = response.text  # Store the raw JSON string
        print(f"Gemini raw response: {full_json_response_string}")

        # Extract only the JSON part to parse it
        json_start = full_json_response_string.find('{')
        json_end = full_json_response_string.rfind('}') + 1

        if json_start != -1 and json_end != -1:
            parsable_json_string = full_json_response_string[json_start:json_end]
            parsed_response = json.loads(parsable_json_string)

            # Create a list of FertilizerRecommendation objects to return
            plan_details_list = [
                FertilizerRecommendation(
                    fertilizer_type=rec['fertilizer_type'],
                    application_stage=rec['application_stage'],
                    quantity_per_acre_kg=rec['quantity_per_acre_kg'],
                    notes=rec['notes']
                ) for rec in parsed_response.get('plan_details', [])
            ]

            # Save the full request context and Gemini's raw JSON response to the database
            new_nutrient_plan_log = NutrientPlan(
                farm_id=request_data.farm_id,
                crop_name=request_data.crop_name,
                soil_type=request_data.soil_type,
                season=request_data.season,
                zone=request_data.zone,
                soil_moisture=sensor_data.soil_moisture,
                soil_temperature=sensor_data.soil_temperature,
                electrical_conductivity=sensor_data.electrical_conductivity,
                soil_ph=sensor_data.soil_ph,
                relative_humidity=sensor_data.relative_humidity,
                solar_radiation=sensor_data.solar_radiation,
                full_plan_json=full_json_response_string  # Save the original JSON string
            )
            db.add(new_nutrient_plan_log)
            db.commit()
            db.refresh(new_nutrient_plan_log)

            return plan_details_list  # Return the parsed list of recommendations
        else:
            print("Gemini response did not contain a valid JSON object for nutrient plan.")
            db.rollback()
            return [
                FertilizerRecommendation(
                    fertilizer_type="Error",
                    application_stage="N/A",
                    quantity_per_acre_kg=0.0,
                    notes="Could not parse API response for nutrient plan."
                )
            ]

    except Exception as e:
        print(f"Error calling Gemini API for nutrient plan generation: {e}")
        db.rollback()  # Rollback changes if an error occurs
        return [
            FertilizerRecommendation(
                fertilizer_type="Error",
                application_stage="N/A",
                quantity_per_acre_kg=0.0,
                notes=f"An issue occurred with the nutrient plan service: {e}"
            )
        ]