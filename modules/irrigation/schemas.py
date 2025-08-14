from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

class IrrigationScheduleRequest(BaseModel):
    """
    Schema for the irrigation schedule request parameters.
    The frontend will provide crop, soil type, and location.
    """
    farm_id: Optional[int] = None # For linking to a specific farm
    crop_name: str
    soil_type: str # e.g., "Loamy Soil", "Sandy Soil"
    latitude: float
    longitude: float

class IrrigationRecommendation(BaseModel):
    """
    A single recommended irrigation event.
    """
    next_irrigation_date: date
    duration_minutes: float # How long to irrigate
    water_amount_mm: float # Equivalent water amount
    reasoning: str # Explanation for the schedule

class IrrigationScheduleResponse(BaseModel):
    """
    Schema for the full irrigation schedule response.
    """
    crop_name: str
    schedule: List[IrrigationRecommendation]
    timestamp: datetime