from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import SensorReading, AccessEvent, VehicleDetection, DroneTelemetry, WeatherReading
from ..config import settings
from datetime import datetime, timedelta
from typing import Optional, List

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/")
async def list_all_events(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    site_id: str = settings.SITE_ID,
    db: Session = Depends(get_db)
):
    """
    Unified endpoint to fetch forensic signals across all 6 source tables.
    """
    # Parse times
    if not end_time:
        end = datetime.utcnow()
    else:
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
    if not start_time:
        start = end - timedelta(hours=24)
    else:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))

    # Fetch from all tables
    results = []
    
    # 1. Sensors
    sensors = db.query(SensorReading).filter(SensorReading.site_id == site_id, SensorReading.recorded_at >= start, SensorReading.recorded_at <= end).all()
    results.extend([{"source": "sensor", "id": str(s.id), "time": s.recorded_at.isoformat(), "zone": s.zone, "type": s.sensor_type, "severity": "high" if s.threshold_breached else "low", "lat": float(s.lat) if s.lat else None, "lon": float(s.lon) if s.lon else None} for s in sensors])
    
    # 2. Access
    access = db.query(AccessEvent).filter(AccessEvent.site_id == site_id, AccessEvent.recorded_at >= start, AccessEvent.recorded_at <= end).all()
    results.extend([{"source": "access", "id": str(a.id), "time": a.recorded_at.isoformat(), "zone": a.zone, "type": a.outcome, "severity": "medium" if a.outcome == 'fail' else "low", "lat": float(a.lat) if a.lat else None, "lon": float(a.lon) if a.lon else None} for a in access])
    
    # 3. Vehicle
    vehicles = db.query(VehicleDetection).filter(VehicleDetection.site_id == site_id, VehicleDetection.recorded_at >= start, VehicleDetection.recorded_at <= end).all()
    results.extend([{"source": "vehicle", "id": str(v.id), "time": v.recorded_at.isoformat(), "zone": v.zone, "type": v.vehicle_type, "severity": "medium" if v.in_restricted else "low", "lat": float(v.lat) if v.lat else None, "lon": float(v.lon) if v.lon else None} for v in vehicles])

    # Sort by time
    results.sort(key=lambda x: x['time'], reverse=True)

    return {
        "count": len(results),
        "window_start": start.isoformat(),
        "window_end": end.isoformat(),
        "events": results
    }
