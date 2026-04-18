from sqlalchemy import Column, String, JSON, ForeignKey
from ..database import Base
import uuid

class DroneMission(Base):
    __tablename__ = "drone_missions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=True)
    path_geojson = Column(JSON) # GeoJSON LineString
    waypoints = Column(JSON) # List of waypoint objects with timestamps and observations
    findings_summary = Column(String, nullable=True)
