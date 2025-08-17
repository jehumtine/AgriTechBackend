# app/modules/nitrate/services.py
import os
import json
import google.generativeai as genai
from sqlalchemy.orm import Session
from datetime import datetime

from modules.nitrate.schemas import NitrateStatusRequest, NitrateStatusResponse
from modules.nitrate.models import NitrateLog
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


def save_nitrate_log(db: Session, farm_id: int, level: float, alert: str, notes: str):
    """
    Saves a nitrate monitoring log entry to the database.
    """
    db_log = NitrateLog(
        farm_id=farm_id,
        nitrate_level_ppm=level,
        risk_level=alert,
        notes=notes
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)


async def get_nitrate_status(
        request_data: NitrateStatusRequest,
        db: Session
) -> NitrateStatusResponse:
    """
    Fetches simulated nitrate levels and uses Gemini to generate a status and notes.
    """
    # 1. Gather simulated sensor data
    sensor_data = get_simulated_sensor_data(request_data.latitude, request_data.longitude)
    current_nitrate_level_ppm = sensor_data.nitrate_ppm  # <-- EXTRACT THE VALUE HERE

    # 2. Construct a prompt for Gemini
    prompt = f"""
    You are a soil and crop expert. Analyze the following nitrate level and provide a status and notes.
    Nitrate Level: {current_nitrate_level_ppm} ppm

    - If the level is between 15-25 ppm, classify it as "Optimal" with notes on maintenance.
    - If the level is below 15 ppm, classify it as "Low" and recommend a light nitrogen fertilizer application.
    - If the level is above 25 ppm, classify it as "High" and advise on potential leaching or crop damage.

    The response must be a JSON object with two keys: "alert" and "notes".

    Example response:
    {{
      "alert": "Optimal",
      "notes": "Current nitrate levels are within the optimal range. No immediate action is required. Monitor regularly."
    }}
    """

    print("Sending nitrate level analysis prompt to Gemini API...")
    try:
        response = await text_model.generate_content_async(prompt)
        response_text = response.text

        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start != -1 and json_end != -1:
            json_response_string = response_text[json_start:json_end]
            parsed_response = json.loads(json_response_string)

            # Save the new log entry to the database
            save_nitrate_log(
                db=db,
                farm_id=request_data.farm_id,
                level=current_nitrate_level_ppm,
                alert=parsed_response['alert'],
                notes=parsed_response['notes']
            )

            return NitrateStatusResponse(
                current_nitrate_level_ppm=current_nitrate_level_ppm,
                alert=parsed_response['alert'],
                notes=parsed_response['notes'],
                timestamp=datetime.now()
            )
        else:
            print("Gemini response did not contain a valid JSON object.")
            db.rollback()
            return NitrateStatusResponse(
                current_nitrate_level_ppm=current_nitrate_level_ppm,
                alert="Processing Error",
                notes="Could not parse API response for nitrate analysis.",
                timestamp=datetime.now()
            )

    except Exception as e:
        print(f"Error calling Gemini API for nitrate analysis: {e}")
        db.rollback()
        return NitrateStatusResponse(
            current_nitrate_level_ppm=current_nitrate_level_ppm,
            alert="Service Error",
            notes=f"An issue occurred with the analysis service: {e}",
            timestamp=datetime.now()
        )