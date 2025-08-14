from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NitrateStatusRequest(BaseModel):
    """
    Schema for the nitrate status request, provided by the frontend.
    """
    latitude: float
    longitude: float
    farm_id: Optional[int] = None

class NitrateAlert(BaseModel):
    """
    Schema for an individual nitrate alert.
    """
    risk_level: str  # e.g., "Low", "Medium", "High"
    message: str     # A detailed message explaining the status and any warnings

class NitrateStatusResponse(BaseModel):
    """
    Schema for the full nitrate monitoring response.
    """
    current_nitrate_level_ppm: float
    timestamp: datetime
    alert: NitrateAlert
    notes: str