# app/modules/nutrient/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models.base import Base # Ensure this import is correct relative to your project structure

class NutrientPlan(Base):
    __tablename__ = "nutrient_plans"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True, nullable=False)

    # Request data (for historical context)
    crop_name = Column(String, nullable=False)
    soil_type = Column(String, nullable=False)
    season = Column(String, nullable=False)
    zone = Column(String, nullable=False)

    # Sensor data used for the request (these columns will be populated from simulated/real sensor data)
    soil_moisture = Column(Float, nullable=True) # Making nullable as sensor data might not always be available
    soil_temperature = Column(Float, nullable=True)
    electrical_conductivity = Column(Float, nullable=True)
    soil_ph = Column(Float, nullable=True)
    relative_humidity = Column(Float, nullable=True)
    solar_radiation = Column(Float, nullable=True)

    # Response data (the full recommendation from Gemini as a JSON string)
    full_plan_json = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to the Farm model
    farm = relationship("Farm", back_populates="nutrient_plans")