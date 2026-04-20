from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import SensorReading, AccessEvent, VehicleDetection, DroneTelemetry, WeatherReading
from ..config import settings
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
import uuid
import os

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/")
async def list_all_events(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    site_id: str = settings.SITE_ID,
    db: Session = Depends(get_db)
):
    """Unified endpoint to fetch forensic signals across heterogeneous source systems."""
    import sqlite3
    import json
    import csv
    import os
    from ..mcp_server.utils import get_data_source_path
    
    if not end_time: end_dt = datetime.utcnow()
    else: end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    
    if not start_time: start_dt = end_dt - timedelta(hours=24)
    else: start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))

    results = []

    # 1. PostgreSQL Source (Sensors & System Metadata)
    sensors = db.query(SensorReading).filter(
        SensorReading.site_id == site_id, 
        SensorReading.recorded_at >= start_dt, 
        SensorReading.recorded_at <= end_dt
    ).all()
    results.extend([{
        "source": "sensor", 
        "format": "postgresql",
        "id": f"pg-{s.id}", 
        "time": s.recorded_at.isoformat(), 
        "zone": s.zone, 
        "type": s.sensor_type, 
        "severity": "high" if s.threshold_breached else "low", 
        "lat": float(s.lat) if s.lat else None, 
        "lon": float(s.lon) if s.lon else None
    } for s in sensors])

    # 2. SQLite Source: Access Control (badge_logs.db)
    badge_db_path = get_data_source_path('badge_logs.db')
    if os.path.exists(badge_db_path):
        try:
            conn = sqlite3.connect(badge_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM badges WHERE site_id = ?", (site_id,))
            for row in cursor.fetchall():
                results.append({
                    "source": "access",
                    "format": "sqlite",
                    "id": f"sq-badge-{row['id']}",
                    "time": row['timestamp'],
                    "zone": row['gate_id'],
                    "type": f"Badge: {row['badge_id']}",
                    "severity": "medium" if row['outcome'] == 'fail' else "low",
                    "lat": 13.0485, # site center default
                    "lon": 77.5435
                })
            conn.close()
        except: pass

    # 3. SQLite Source: Vehicle Tracking (vehicle_logs.db)
    vehicle_db_path = get_data_source_path('vehicle_logs.db')
    if os.path.exists(vehicle_db_path):
        try:
            conn = sqlite3.connect(vehicle_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vehicles WHERE site_id = ?", (site_id,))
            for row in cursor.fetchall():
                results.append({
                    "source": "vehicle",
                    "format": "sqlite",
                    "id": f"sq-veh-{row['id']}",
                    "time": row['timestamp'],
                    "zone": row['zone'],
                    "type": f"Vehicle: {row['vehicle_id']}",
                    "severity": "high" if row['is_restricted'] else "low",
                    "lat": row['lat'],
                    "lon": row['lon']
                })
            conn.close()
        except: pass

    # 4. JSON Source: Weather API (weather_api.json)
    weather_path = get_data_source_path('weather_api.json')
    if os.path.exists(weather_path):
        try:
            with open(weather_path, 'r') as f:
                weather_data = json.load(f)
                for wd in weather_data:
                    if wd['site_id'] == site_id:
                        results.append({
                            "source": "weather",
                            "format": "json",
                            "id": f"js-wea-{hash(wd['timestamp'])}",
                            "time": wd['timestamp'],
                            "zone": "Site-Wide",
                            "type": wd['raw_value'],
                            "severity": "medium" if "STORM" in wd['raw_value'] else "low",
                            "lat": 13.0485,
                            "lon": 77.5435
                        })
        except: pass

    # 5. CSV Source: Shift Schedule (shift_schedule.csv)
    shift_path = get_data_source_path('shift_schedule.csv')
    if os.path.exists(shift_path):
        try:
            with open(shift_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['site_id'] == site_id:
                        results.append({
                            "source": "shift",
                            "format": "csv",
                            "id": f"cv-shf-{row['staff_id']}",
                            "time": f"{row['date']}T{row['shift_start']}Z",
                            "zone": row['zone'],
                            "type": f"Staff: {row['staff_id']} ({row['role']})",
                            "severity": "low",
                            "lat": 13.0485,
                            "lon": 77.5435
                        })
        except: pass

    results.sort(key=lambda x: x['time'], reverse=True)
    return {"count": len(results), "events": results}


@router.get("/sensors")
async def list_sensors(db: Session = Depends(get_db)):
    return db.query(SensorReading).order_by(SensorReading.recorded_at.desc()).limit(100).all()

@router.get("/access")
async def list_access(site_id: str = settings.SITE_ID, db: Session = Depends(get_db)):
    # 1. Fetch from PostgreSQL
    pg_results = db.query(AccessEvent).filter(AccessEvent.site_id == site_id)\
        .order_by(AccessEvent.recorded_at.desc()).limit(100).all()
    
    results = []
    for a in pg_results:
        results.append({
            "id": str(a.id),
            "outcome": a.outcome,
            "badge_id": a.badge_id,
            "gate_id": a.gate_id,
            "recorded_at": a.recorded_at.isoformat() + "Z",
            "timestamp": a.recorded_at.isoformat() + "Z",
            "source": "postgresql"
        })

    # 2. Fetch from SQLite
    import sqlite3
    from ..mcp_server.utils import get_data_source_path
    badge_path = get_data_source_path('badge_logs.db')
    if os.path.exists(badge_path):
        try:
            conn = sqlite3.connect(badge_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM badges WHERE site_id = ? ORDER BY timestamp DESC LIMIT 50", (site_id,))
            for row in c.fetchall():
                results.append({
                    "id": f"sq-acc-{row['id']}",
                    "outcome": row['outcome'],
                    "badge_id": row['badge_id'],
                    "gate_id": row['gate_id'],
                    "recorded_at": row['timestamp'],
                    "timestamp": row['timestamp'],
                    "source": "sqlite"
                })
            conn.close()
        except: pass

    results.sort(key=lambda x: x['recorded_at'], reverse=True)
    return results

@router.get("/vehicles")
async def list_vehicles(site_id: str = settings.SITE_ID, db: Session = Depends(get_db)):
    # 1. Fetch from PostgreSQL
    pg_results = db.query(VehicleDetection).filter(VehicleDetection.site_id == site_id)\
        .order_by(VehicleDetection.recorded_at.desc()).limit(100).all()
    
    results = []
    for v in pg_results:
        results.append({
            "id": str(v.id),
            "vehicle_id": v.vehicle_id,
            "vehicle_type": v.vehicle_type,
            "in_restricted": v.in_restricted,
            "recorded_at": v.recorded_at.isoformat() + "Z",
            "timestamp": v.recorded_at.isoformat() + "Z",
            "source": "postgresql"
        })

    # 2. Fetch from SQLite
    import sqlite3
    from ..mcp_server.utils import get_data_source_path
    veh_path = get_data_source_path('vehicle_logs.db')
    if os.path.exists(veh_path):
        try:
            conn = sqlite3.connect(veh_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM vehicles WHERE site_id = ? ORDER BY timestamp DESC LIMIT 50", (site_id,))
            for row in c.fetchall():
                results.append({
                    "id": f"sq-veh-{row['id']}",
                    "vehicle_id": row['vehicle_id'],
                    "vehicle_type": "unknown",
                    "in_restricted": bool(row['is_restricted']),
                    "recorded_at": row['timestamp'],
                    "timestamp": row['timestamp'],
                    "source": "sqlite"
                })
            conn.close()
        except: pass

    results.sort(key=lambda x: x['recorded_at'], reverse=True)
    return results

@router.get("/drones")
async def list_drones(site_id: str = settings.SITE_ID, db: Session = Depends(get_db)):
    # 1. Fetch from PostgreSQL
    pg_results = db.query(DroneTelemetry).filter(DroneTelemetry.site_id == site_id)\
        .order_by(DroneTelemetry.recorded_at.desc()).limit(100).all()
    
    results = []
    for d in pg_results:
        results.append({
            "id": str(d.id),
            "mission_id": d.mission_id,
            "drone_id": d.drone_id,
            "observation": d.observation,
            "recorded_at": d.recorded_at.isoformat() + "Z",
            "timestamp": d.recorded_at.isoformat() + "Z",
            "source": "postgresql"
        })

    # 2. Fetch from JSON
    import json
    from ..mcp_server.utils import get_data_source_path
    drone_path = get_data_source_path('drone_logs.json')
    if os.path.exists(drone_path):
        try:
            with open(drone_path, 'r') as f:
                data = json.load(f)
                for d in data:
                    results.append({
                        "id": f"js-drn-{hash(d['timestamp'])}",
                        "mission_id": d['mission_id'],
                        "drone_id": "DRN-SYS-EXT",
                        "observation": d['observation'],
                        "recorded_at": d['timestamp'],
                        "timestamp": d['timestamp'],
                        "source": "json"
                    })
        except: pass

    results.sort(key=lambda x: x['recorded_at'], reverse=True)
    return results

@router.get("/weather")
async def list_weather():
    from ..mcp_server.utils import get_data_source_path
    import json
    import os
    path = get_data_source_path('weather_api.json')
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)[-100:]
            for i, d in enumerate(data):
                if 'id' not in d:
                    d['id'] = f"wea-{d.get('timestamp', i)}"
            return data
    return []

@router.get("/debug/files")
async def debug_files():
    from ..mcp_server.utils import get_data_source_path
    import os
    files = ['weather_api.json', 'drone_logs.json', 'badge_logs.db', 'vehicle_logs.db', 'shift_schedule.csv']
    results = {}
    for f in files:
        path = get_data_source_path(f)
        results[f] = {
            "path": path,
            "exists": os.path.exists(path)
        }
    return results

@router.get("/personnel")
async def list_personnel():
    from ..mcp_server.utils import get_data_source_path
    import csv
    import os
    path = get_data_source_path('shift_schedule.csv')
    if os.path.exists(path):
        results = []
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                row['id'] = f"shf-{row.get('staff_id', i)}-{i}"
                results.append(row)
        return results[::-1][:100]
    return []

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
async def seed_live_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generates forensic events across ALL formats and AUTO-TRIGGERS Maya's investigation."""
    import random
    import sqlite3
    import json
    import csv
    import os
    from ..mcp_server.utils import get_data_source_path
    from .investigate import start_investigation
    
    base_lat, base_lon = 13.0485, 77.5435
    now = datetime.utcnow()
    now_iso = now.isoformat() + "Z"
    
    # Generate 5 PostgreSQL high-severity trigger signals
    for _ in range(5):
        l, ln = base_lat + random.uniform(-0.003, 0.003), base_lon + random.uniform(-0.003, 0.003)
        e = SensorReading(
            site_id=settings.SITE_ID, 
            recorded_at=now, 
            sensor_id=f"S-{uuid.uuid4().hex[:4]}", 
            sensor_type=random.choice(["vibration", "motion", "perimeter"]), 
            zone=random.choice(["block-a", "block-b", "perimeter"]), 
            raw_value=0.9, 
            threshold=0.5, 
            threshold_breached=True, 
            lat=l, lon=ln
        )
        db.add(e)
    
    # Seed SQLite: Access Control
    badge_path = get_data_source_path('badge_logs.db')
    if os.path.exists(badge_path):
        try:
            conn = sqlite3.connect(badge_path)
            c = conn.cursor()
            c.execute("INSERT INTO badges (badge_id, site_id, gate_id, timestamp, outcome) VALUES (?, ?, ?, ?, ?)",
                     (f"STAFF-{random.randint(100,999)}", settings.SITE_ID, "main-gate", now_iso, random.choice(['success', 'fail'])))
            conn.commit()
            conn.close()
        except: pass

    # Seed SQLite: Vehicle Tracking
    veh_path = get_data_source_path('vehicle_logs.db')
    if os.path.exists(veh_path):
        try:
            conn = sqlite3.connect(veh_path)
            c = conn.cursor()
            l, ln = base_lat + random.uniform(-0.003, 0.003), base_lon + random.uniform(-0.003, 0.003)
            c.execute("INSERT INTO vehicles (vehicle_id, site_id, zone, timestamp, lat, lon, is_restricted) VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (f"KA-0{random.randint(1,9)}-Z-{random.randint(1000,9999)}", settings.SITE_ID, "restricted-zone", now_iso, l, ln, 1))
            conn.commit()
            conn.close()
        except: pass

    # Seed JSON: Weather
    weather_path = get_data_source_path('weather_api.json')
    if os.path.exists(weather_path):
        try:
            with open(weather_path, 'r+') as f:
                data = json.load(f)
                data.append({
                    "site_id": settings.SITE_ID,
                    "timestamp": now_iso,
                    "type": "weather",
                    "wind_speed": random.uniform(5, 50),
                    "visibility": random.randint(100, 2000),
                    "precipitation": random.uniform(0, 10),
                    "raw_value": f"AUTO-GEN: {random.randint(5,50)}km/h Winds"
                })
                f.seek(0)
                json.dump(data[-20:], f, indent=4)
                f.truncate()
        except: pass

    # Seed JSON: Drone Logs
    drone_path = get_data_source_path('drone_logs.json')
    if os.path.exists(drone_path):
        try:
            with open(drone_path, 'r+') as f:
                data = json.load(f)
                l, ln = base_lat + random.uniform(-0.003, 0.003), base_lon + random.uniform(-0.003, 0.003)
                data.append({
                    "mission_id": f"M-{random.randint(100,999)}",
                    "timestamp": now_iso,
                    "lat": l, "lon": ln,
                    "observation": "Auto-generated patrol observation: All clear.",
                    "confidence": 0.9,
                    "type": "drone_observation"
                })
                f.seek(0)
                json.dump(data[-20:], f, indent=4)
                f.truncate()
        except: pass

    # Seed CSV: Shift
    shift_path = get_data_source_path('shift_schedule.csv')
    if os.path.exists(shift_path):
        try:
            with open(shift_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([now.strftime('%Y-%m-%d'), settings.SITE_ID, f"GEN-{random.randint(10,99)}", "Contractor", "Global", "00:00:00", "23:59:59"])
        except: pass

    db.commit()
    
    # AUTONOMOUS CHAIN: Wake up Maya to investigate the fresh data immediately
    print(f"[*] Seeding complete. Maya is waking up to investigate fresh signals...")
    background_tasks.add_task(start_investigation, background_tasks, db)
    
    return {"status": "seeded_and_scan_triggered", "count": 10}


