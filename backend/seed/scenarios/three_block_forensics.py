from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session
from app.models.sensor_readings import SensorReading
from app.models.access_events import AccessEvent
from app.models.vehicle_detections import VehicleDetection
from app.models.drone_telemetry import DroneTelemetry
from app.models.weather_readings import WeatherReading
from app.models.site_metadata import SiteZone, ShiftSchedule

def seed_three_block_scenario(db: Session, site_id: str):
    # 1. Setup Zones
    zones = [
        SiteZone(site_id=site_id, zone_id="block-a", zone_name="Logistics & Receiving", zone_type="workzone", is_restricted=False, expected_vehicles=True),
        SiteZone(site_id=site_id, zone_id="block-b", zone_name="Solar Array & Utility", zone_type="perimeter", is_restricted=False),
        SiteZone(site_id=site_id, zone_id="block-c", zone_name="Research Lab & Server", zone_type="restricted", is_restricted=True, access_rules={"allowed_roles": ["admin", "security"]})
    ]
    for z in zones: db.add(z)
    db.flush()

    # 2. Setup Shift
    now = datetime.utcnow()
    tonight = now.replace(hour=22, minute=0, second=0, microsecond=0) - timedelta(days=1)
    db.add(ShiftSchedule(
        site_id=site_id,
        shift_date=tonight.date(),
        shift_type="night",
        shift_start=tonight,
        shift_end=tonight + timedelta(hours=8),
        supervisor_id="SUP-8821",
        headcount=4,
        active_zones=["block-a"]
    ))

    # 3. Weather Log (24 buckets @ 15m) -- BLOCK B Focus (Windy)
    for i in range(24):
        time = tonight + timedelta(minutes=i*15)
        wind = 32 if 8 <= i <= 14 else 12 # Spike in the middle of the night
        db.add(WeatherReading(
            site_id=site_id,
            recorded_at=time,
            wind_kmh=wind,
            gust_kmh=wind + 8,
            temp_c=22.5,
            visibility_m=10000,
            precipitation="none"
        ))

    # 4. BLOCK A: Standard Logistics (Vehicle + Access)
    vehicle_path_id = "path-99"
    for i in range(5):
        db.add(VehicleDetection(
            site_id=site_id,
            recorded_at=tonight + timedelta(minutes=10+i),
            zone="block-a",
            vehicle_id="FRK-01",
            vehicle_type="forklift",
            lat=12.9716 + (i * 0.0001),
            lon=77.5946,
            speed_kmh=12,
            in_restricted=False,
            path_segment_id=vehicle_path_id
        ))
    db.add(AccessEvent(site_id=site_id, recorded_at=tonight + timedelta(minutes=12), gate_id="GATE-A1", zone="block-a", badge_id="EMP-100", outcome="success", lat=12.9716, lon=77.5946))

    # 5. BLOCK B: Environmental Triggers (Sensor)
    db.add(SensorReading(
        site_id=site_id, 
        recorded_at=tonight + timedelta(hours=2, minutes=30), 
        zone="block-b", 
        sensor_id="FEN-B-09", 
        sensor_type="fence_vibration", 
        raw_value=18, 
        threshold=15, 
        threshold_breached=True, # Windy but no breach
        lat=12.9720, lon=77.5950
    ))

    # 6. BLOCK C: SECURITY INCIDENT (The core investigation)
    # 6a. Failed Access
    db.add(AccessEvent(
        site_id=site_id, 
        recorded_at=tonight + timedelta(hours=3, minutes=12), 
        gate_id="GATE-C-SEC", 
        zone="block-c", 
        badge_id="UNKNOWN-77", 
        outcome="fail", 
        failure_reason="unknown_badge",
        lat=12.9730, lon=77.5960
    ))
    # 6b. Fence Breach
    db.add(SensorReading(
        site_id=site_id, 
        recorded_at=tonight + timedelta(hours=3, minutes=15), 
        zone="block-c", 
        sensor_id="FEN-C-01", 
        sensor_type="perimeter", 
        raw_value=1, 
        threshold=0, 
        threshold_breached=True,
        lat=12.9731, lon=77.5961
    ))
    # 6c. Vehicle in Restricted
    restricted_v_id = "path-hazard"
    for i in range(3):
        db.add(VehicleDetection(
            site_id=site_id,
            recorded_at=tonight + timedelta(hours=3, minutes=16+i),
            zone="block-c",
            vehicle_id="VAN-99",
            vehicle_type="truck",
            lat=12.9732 + (i * 0.0001),
            lon=77.5962,
            speed_kmh=15,
            in_restricted=True,
            path_segment_id=restricted_v_id
        ))
    # 6d. Drone Telemetry (Scheduled patrol that flags the truck)
    mission_id = "MIS-202"
    for i in range(10):
        flagged = True if i == 5 else False
        db.add(DroneTelemetry(
            site_id=site_id,
            recorded_at=tonight + timedelta(hours=3, minutes=10 + i),
            mission_id=mission_id,
            mission_type="scheduled",
            drone_id="DRONE-01",
            lat=12.9730 + (i * 0.0001),
            lon=77.5960,
            altitude_m=35.0,
            flagged=flagged,
            flag_reason="Unknown vehicle in lab zone" if flagged else None,
            observation="Routine scan"
        ))

    db.commit()
    print(f"Successfully seeded 3-block scenario for site {site_id}")
