from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import uuid4
from datetime import datetime
from ..database import Base

class DroneMission(Base):
    __tablename__ = "drone_missions"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at      = Column(DateTime(timezone=True), default=datetime.utcnow)
    incident_id     = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    mission_status  = Column(String(32), default="pending")
    # mission_status: pending | flying | completed | failed
    
    path_geojson    = Column(JSONB)
    waypoints       = Column(JSONB)
    findings        = Column(Text)
    metadata_json   = Column(JSONB, default={})
