from datetime import datetime
from pydantic import BaseModel

class SoilAnalysisResponse(BaseModel):
    """
    Pydantic schema for the soil analysis API response.
    This defines the expected format of the data returned to the client.
    """
    id: int
    image_filename: str
    predicted_soil_type: str
    confidence: float
    analysis_timestamp: datetime

    class Config:
        from_attributes = True # This allows conversion from the SQLAlchemy ORM model to the Pydantic model.