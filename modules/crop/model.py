from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class CropRecommendation(Base):
    __tablename__ = "crop_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)

    # Inputs used for the request
    soil_type = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Sensor data used for the request (populated internally)
    soil_moisture = Column(Float, nullable=True)
    soil_temperature = Column(Float, nullable=True)
    electrical_conductivity = Column(Float, nullable=True)
    soil_ph = Column(Float, nullable=True)
    relative_humidity = Column(Float, nullable=True)
    solar_radiation = Column(Float, nullable=True)
    nitrate_ppm = Column(Float, nullable=True)

    # Response data (the full recommendation from Gemini)
    recommended_crop = Column(String, nullable=False)
    reasoning = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to the Farm model
    farm = relationship("Farm", back_populates="crop_recommendations")