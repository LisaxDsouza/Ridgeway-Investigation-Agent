from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import uuid4
from datetime import datetime
from ..database import Base

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    recorded_at         = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    site_id             = Column(String(64), nullable=False)
    zone                = Column(String(64), nullable=False)
    sensor_id           = Column(String(128), nullable=False)
    sensor_type         = Column(String(64), nullable=False)
    # sensor_type values: fence_vibration | motion | perimeter | env_temp | env_wind
    raw_value           = Column(Numeric)
    unit                = Column(String(32))
    threshold           = Column(Numeric)
    threshold_breached  = Column(Boolean, nullable=False, default=False)
    lat                 = Column(Numeric(10, 7))
    lon                 = Column(Numeric(10, 7))
    incident_id         = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    metadata_json       = Column(JSONB, default={})
