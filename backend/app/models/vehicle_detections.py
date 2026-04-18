from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import uuid4
from datetime import datetime
from ..database import Base

class VehicleDetection(Base):
    __tablename__ = "vehicle_detections"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    recorded_at         = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    site_id             = Column(String(64), nullable=False)
    zone                = Column(String(64), nullable=False)
    vehicle_id          = Column(String(128))
    vehicle_type        = Column(String(64))
    # vehicle_type: truck | forklift | car | drone | unknown
    lat                 = Column(Numeric(10, 7))
    lon                 = Column(Numeric(10, 7))
    speed_kmh           = Column(Numeric(5, 2))
    in_restricted       = Column(Boolean, default=False)
    path_segment_id     = Column(String(128)) # Used to group points into a path
    incident_id         = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    metadata_json       = Column(JSONB, default={})
