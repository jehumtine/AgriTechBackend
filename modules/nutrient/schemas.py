from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class NutrientPlanRequest(BaseModel):
    """
    Schema for the nutrient plan request parameters provided by the frontend.
    """
    crop_name: str
    soil_type: str
    season: str
    zone: str
    latitude: float
    longitude: float

class InternalNutrientPlanRequest(BaseModel):
    """
    An internal schema used by the service layer, containing all data
    including the simulated sensor readings.
    """
    crop_name: str
    soil_type: str
    season: str
    zone: str
    latitude: float
    longitude: float
    soil_moisture: float
    soil_temperature: float
    electrical_conductivity: float
    soil_ph: float
    relative_humidity: float
    solar_radiation: float
    farm_id: Optional[int] = None

class FertilizerRecommendation(BaseModel):
    """
    A single recommendation for a fertilizer application.
    """
    fertilizer_type: str
    application_stage: str
    quantity_per_acre_kg: float
    notes: str

class NutrientPlanResponse(BaseModel):
    """
    Schema for the full nutrient plan response.
    """
    crop_name: str
    plan_details: List[FertilizerRecommendation]
    timestamp: datetime