from sqlalchemy.orm import Session
from datetime import datetime
from ..models import Event
from typing import List, Optional

def retrieve_sensor_events(db: Session, start_time: datetime, end_time: datetime, zone: Optional[str] = None):
    """
    List of sensor events: type, timestamp, location, raw_value
    """
    query = db.query(Event).filter(
        Event.source == "sensor",
        Event.timestamp >= start_time,
        Event.timestamp <= end_time
    )
    # Note: Zone filtering would use spatial query in production
    return [e.__dict__ for e in query.all()]

def retrieve_access_logs(db: Session, start_time: datetime, end_time: datetime, gate: Optional[str] = None):
    """
    Badge swipe events: outcome (success/fail), badge_id, gate_id
    """
    query = db.query(Event).filter(
        Event.source == "gate_access",
        Event.timestamp >= start_time,
        Event.timestamp <= end_time
    )
    return [e.__dict__ for e in query.all()]

def retrieve_vehicle_events(db: Session, start_time: datetime, end_time: datetime, zone: Optional[str] = None):
    """
    Vehicle detections: vehicle_id, location, speed, direction
    """
    query = db.query(Event).filter(
        Event.source == "vehicle_tracking",
        Event.timestamp >= start_time,
        Event.timestamp <= end_time
    )
    return [e.__dict__ for e in query.all()]

def retrieve_drone_logs(db: Session, mission_id: Optional[str] = None):
    """
    Patrol log: full path GeoJSON, per-waypoint observations, flags
    """
    # In MVP, this might pull from a different model or table
    # For now, placeholder returning empty list
    return []
