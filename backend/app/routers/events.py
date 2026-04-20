from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import SensorReading, AccessEvent, VehicleDetection, DroneTelemetry, WeatherReading
from ..config import settings
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/")
async def list_all_events(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    site_id: str = settings.SITE_ID,
    db: Session = Depends(get_db)
):
    """Unified endpoint to fetch forensic signals across source tables."""
    if not end_time: end = datetime.utcnow()
    else: end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    if not start_time: start = end - timedelta(hours=24)
    else: start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))

    results = []
    sensors = db.query(SensorReading).filter(SensorReading.site_id == site_id, SensorReading.recorded_at >= start, SensorReading.recorded_at <= end).all()
    results.extend([{"source": "sensor", "id": str(s.id), "time": s.recorded_at.isoformat(), "zone": s.zone, "type": s.sensor_type, "severity": "high" if s.threshold_breached else "low", "lat": float(s.lat) if s.lat else None, "lon": float(s.lon) if s.lon else None} for s in sensors])
    access = db.query(AccessEvent).filter(AccessEvent.site_id == site_id, AccessEvent.recorded_at >= start, AccessEvent.recorded_at <= end).all()
    results.extend([{"source": "access", "id": str(a.id), "time": a.recorded_at.isoformat(), "zone": a.zone, "type": a.outcome, "severity": "medium" if a.outcome == 'fail' else "low", "lat": float(a.lat) if a.lat else None, "lon": float(a.lon) if a.lon else None} for a in access])
    vehicles = db.query(VehicleDetection).filter(VehicleDetection.site_id == site_id, VehicleDetection.recorded_at >= start, VehicleDetection.recorded_at <= end).all()
    results.extend([{"source": "vehicle", "id": str(v.id), "time": v.recorded_at.isoformat(), "zone": v.zone, "type": v.vehicle_type, "severity": "medium" if v.in_restricted else "low", "lat": float(v.lat) if v.lat else None, "lon": float(v.lon) if v.lon else None} for v in vehicles])
    results.sort(key=lambda x: x['time'], reverse=True)
    return {"count": len(results), "events": results}

@router.get("/sensors")
async def list_sensors(db: Session = Depends(get_db)):
    return db.query(SensorReading).order_by(SensorReading.recorded_at.desc()).limit(100).all()

@router.get("/access")
async def list_access(db: Session = Depends(get_db)):
    return db.query(AccessEvent).order_by(AccessEvent.recorded_at.desc()).limit(100).all()

@router.get("/vehicles")
async def list_vehicles(db: Session = Depends(get_db)):
    return db.query(VehicleDetection).order_by(VehicleDetection.recorded_at.desc()).limit(100).all()

@router.get("/drones")
async def list_drones(db: Session = Depends(get_db)):
    return db.query(DroneTelemetry).order_by(DroneTelemetry.recorded_at.desc()).limit(100).all()

class IngestSignal(BaseModel):
    source: str # 'sensor', 'access', 'vehicle'
    type: str
    zone: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    data: Optional[dict] = {}

@router.post("/ingest")
async def ingest_signal(
    signal: IngestSignal, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Ingest a forensic signal. If it's a high-severity breach, Maya automatically starts investigating.
    """
    from .investigate import start_investigation
    
    now = datetime.utcnow()
    is_trigger = False
    
    if signal.source == 'sensor':
        new_event = SensorReading(
            site_id=settings.SITE_ID,
            recorded_at=now,
            sensor_id=f"MANUAL-{uuid.uuid4().hex[:4]}",
            sensor_type=signal.type,
            zone=signal.zone,
            raw_value=1.0,
            threshold=0.0,
            threshold_breached=True,
            lat=signal.lat,
            lon=signal.lon
        )
        is_trigger = True
    elif signal.source == 'access':
        new_event = AccessEvent(
            site_id=settings.SITE_ID,
            recorded_at=now,
            gate_id=f"GATE-{signal.zone}",
            zone=signal.zone,
            badge_id=signal.data.get('badge_id', 'UNKNOWN'),
            outcome=signal.type,
            lat=signal.lat,
            lon=signal.lon
        )
        if signal.type == 'fail': is_trigger = True
    else: # vehicle
        new_event = VehicleDetection(
            site_id=settings.SITE_ID,
            recorded_at=now,
            zone=signal.zone,
            vehicle_id=signal.data.get('vehicle_id', 'UNKNOWN'),
            vehicle_type=signal.type,
            in_restricted=True,
            lat=signal.lat,
            lon=signal.lon
        )
        is_trigger = True
        
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    # AUTONOMOUS ACTION: If it's a breach, wake up Maya immediately
    if is_trigger:
        print(f"[*] Autonomous Trigger: Maya is waking up to investigate {signal.type} @ {signal.zone}")
        background_tasks.add_task(start_investigation, background_tasks, db)
        
@router.post("/seed")
async def seed_live_data(db: Session = Depends(get_db)):
    """Generates a small batch of random forensic events for testing."""
    import random
    from .investigate import start_investigation
    
    base_lat, base_lon = 13.0485, 77.5435
    now = datetime.utcnow()
    new_ids = []
    
    # Generate 10 random events
    for _ in range(10):
        src = random.choice(['sensor', 'access', 'vehicle', 'drone'])
        l, ln = base_lat + random.uniform(-0.003, 0.003), base_lon + random.uniform(-0.003, 0.003)
        
        if src == 'sensor':
            e = SensorReading(site_id=settings.SITE_ID, recorded_at=now, sensor_id=f"S-{uuid.uuid4().hex[:4]}", sensor_type="vibration", zone="HMT-Perimeter", raw_value=0.9, threshold=0.5, threshold_breached=True, lat=l, lon=ln)
        elif src == 'access':
            e = AccessEvent(site_id=settings.SITE_ID, recorded_at=now, gate_id="HMT-Staff-Gate", zone="HMT-Entry", badge_id=f"STAFF-{random.randint(100,999)}", outcome=random.choice(['success', 'fail']), lat=l, lon=ln)
        elif src == 'vehicle':
            e = VehicleDetection(site_id=settings.SITE_ID, recorded_at=now, vehicle_id=f"V-{random.randint(100,999)}", vehicle_type="van", zone="HMT-Loading", in_restricted=True, lat=l, lon=ln)
        else:
            e = DroneTelemetry(site_id=settings.SITE_ID, recorded_at=now, mission_id="M-LIVE", drone_id="D-01", lat=l, lon=ln, altitude_m=25.0, observation="Active sweep...", flagged=False)
            
        db.add(e)
        new_ids.append(str(e.id))
        
    db.commit()
    return {"status": "seeded", "count": 10}
