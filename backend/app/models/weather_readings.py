from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import uuid4
from datetime import datetime
from ..database import Base

class WeatherReading(Base):
    __tablename__ = "weather_readings"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    recorded_at         = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    site_id             = Column(String(64), nullable=False)
    temp_c              = Column(Numeric(4, 1))
    wind_kmh            = Column(Numeric(5, 2))
    gust_kmh            = Column(Numeric(5, 2))
    precipitation       = Column(String(64))
    # precipitation: none | rain | snow | hail
    visibility_m        = Column(Numeric(8, 2))
    incident_id         = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    metadata_json       = Column(JSONB, default={})
