# app/modules/crop/schemas.py
from pydantic import BaseModel
from typing import List
from datetime import datetime

class RecommendationRequest(BaseModel):
    """
    Pydantic schema for the crop recommendation request parameters,
    now simplified to only require location.
    """
    latitude: float
    longitude: float

class SensorData(BaseModel):
    """
    Schema for the detailed sensor data collected by the backend.
    This is an internal schema used by the service layer.
    """
    latitude: float
    longitude: float
    soil_moisture: float
    soil_temperature: float
    electrical_conductivity: float
    soil_ph: float
    relative_humidity: float
    solar_radiation: float

class CropRecommendation(BaseModel):
    """
    Schema for an individual crop recommendation from the Gemini API.
    """
    crop_name: str
    reasoning: str # Provides a detailed explanation for the recommendation
    suitability_score: float # A score from 0 to 1, indicating suitability

class RecommendationResponse(BaseModel):
    """
    Schema for the full crop recommendation response.
    """
    recommendations: List[CropRecommendation]
    timestamp: datetime