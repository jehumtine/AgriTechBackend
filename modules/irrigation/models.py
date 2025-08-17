from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models.base import Base


class IrrigationSchedule(Base):
    __tablename__ = "irrigation_schedules"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True, nullable=False)

    crop_name = Column(String, nullable=False)
    scheduled_date = Column(Date, nullable=False)
    duration_minutes = Column(Float, nullable=False)
    water_amount_mm = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=True)
    status = Column(String, default="scheduled", nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    farm = relationship("Farm", back_populates="irrigation_schedules")