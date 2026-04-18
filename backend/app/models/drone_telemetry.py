from sqlalchemy import Column, String, Numeric, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import uuid4
from datetime import datetime
from ..database import Base

class DroneTelemetry(Base):
    __tablename__ = "drone_telemetry"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    recorded_at         = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    site_id             = Column(String(64), nullable=False)
    mission_id          = Column(String(128))
    mission_type        = Column(String(64))
    # mission_type: scheduled | follow_up | manual
    drone_id            = Column(String(128))
    lat                 = Column(Numeric(10, 7))
    lon                 = Column(Numeric(10, 7))
    altitude_m          = Column(Numeric(6, 2))
    heading             = Column(Integer)
    waypoint_index      = Column(Integer)
    flagged             = Column(Boolean, default=False)
    flag_reason         = Column(String(256))
    observation         = Column(Text)
    incident_id         = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    metadata_json       = Column(JSONB, default={})
