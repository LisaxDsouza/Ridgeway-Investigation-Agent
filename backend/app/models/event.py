from sqlalchemy import Column, String, DateTime, JSON, Float
from sqlalchemy.sql import func
from ..database import Base
import uuid

class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    event_type = Column(String, index=True)  # fence_vibration, failed_badge, vehicle_speed, etc.
    source = Column(String)  # sensor, gate_access, drone_patrol
    lat = Column(Float)
    lon = Column(Float)
    metadata_json = Column(JSON, default={})  # store extra info like badge_id, vehicle_id, etc.
    incident_id = Column(String, index=True, nullable=True) # Linked after clustering
