from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base
from modules.auth.models import User
from modules.nitrate.models import NitrateLog
from modules.irrigation.models import IrrigationSchedule
from modules.nutrient.model import NutrientPlan
from modules.crop.model import CropRecommendation


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    location_name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="farms")

    # 🧪 Relationships with our new AI-generated modules
    nitrate_logs = relationship("NitrateLog", back_populates="farm")
    irrigation_schedules = relationship("IrrigationSchedule", back_populates="farm")
    nutrient_plans = relationship("NutrientPlan", back_populates="farm")
    crop_recommendations = relationship("CropRecommendation", back_populates="farm")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())