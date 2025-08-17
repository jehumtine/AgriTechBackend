from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models.base import Base


class NitrateLog(Base):
    __tablename__ = "nitrate_logs"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), index=True, nullable=False)

    nitrate_level_ppm = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    alert_message = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    checked_at = Column(DateTime(timezone=True), server_default=func.now())

    farm = relationship("Farm", back_populates="nitrate_logs")