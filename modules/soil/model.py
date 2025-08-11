from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from models.base import Base

class SoilAnalysis(Base):
    """
    SQLAlchemy model for storing the results of soil analysis.
    This table will be used to persist the predictions made by the API.
    """
    __tablename__ = "soil_analysis"

    id = Column(Integer, primary_key=True, index=True)
    image_filename = Column(String, nullable=False)
    predicted_soil_type = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    analysis_timestamp = Column(DateTime(timezone=True), server_default=func.now())
