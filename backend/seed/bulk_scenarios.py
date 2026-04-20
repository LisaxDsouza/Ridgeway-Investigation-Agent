import os
import sys
import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the parent directory to sys.path to allow imports from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import (
    SensorReading, AccessEvent, VehicleDetection, 
    DroneTelemetry, WeatherReading
)

def bulk_seed():
    db = SessionLocal()
    site_id = "ridgeway-01"
    now = datetime.utcnow()
    
    print(f"Generating 50+ diverse forensic scenarios for {site_id}...")
    
    zones = ["Block-A", "Block-B", "Block-C", "North-Gate", "West-Gate", "South-Perimeter"]
    sensor_types = ["vibration", "motion", "thermal", "laser_grid"]
    
    try:
        for i in range(50):
            # Pick a random day in the last 30 days
            days_ago = random.randint(0, 30)
            hour = random.randint(0, 23)
            base_time = now - timedelta(days=days_ago, hours=hour)
            
            scenario_type = random.choice(["routine", "false_alarm", "minor_breach", "contractor_visit"])
            
            base_lat, base_lon = 13.0485, 77.5435
            # Tight square radius for HMT Factory area (+/- 0.003)
            lat_off = lambda: random.uniform(-0.003, 0.003)
            lon_off = lambda: random.uniform(-0.003, 0.003)

            if scenario_type == "routine":
                # Successful badge in/out
                zone = random.choice(["North-Gate", "West-Gate"])
                badge_id = f"STAFF-{random.randint(1000, 9999)}"
                
                db.add(AccessEvent(
                    site_id=site_id, recorded_at=base_time, gate_id=f"G-{zone}", 
                    zone=zone, badge_id=badge_id, person_id="STAFF-USER", 
                    outcome="success", 
                    lat=base_lat + lat_off(), 
                    lon=base_lon + lon_off()
                ))
                
            elif scenario_type == "false_alarm":
                # Vibration sensor followed by a drone 'clear' check
                zone = random.choice(["South-Perimeter", "Block-C"])
                l1, ln1 = base_lat + lat_off(), base_lon + lon_off()
                db.add(SensorReading(
                    site_id=site_id, recorded_at=base_time, sensor_id=f"S-{uuid.uuid4().hex[:4]}",
                    sensor_type="vibration", zone=zone, raw_value=0.8, threshold=0.5, 
                    threshold_breached=True, lat=l1, lon=ln1
                ))
                db.add(DroneTelemetry(
                    site_id=site_id, recorded_at=base_time + timedelta(minutes=5), 
                    mission_id=f"M-{uuid.uuid4().hex[:4]}", drone_id="D-01", 
                    lat=l1 + 0.0001, lon=ln1 + 0.0001, altitude_m=30.0, 
                    observation="Thermal scan: Wildlife detected (Deer). No breach.", 
                    flagged=True, flag_reason="Thermal Anomaly"
                ))
                
            elif scenario_type == "minor_breach":
                # Badge failure + restricted vehicle
                zone = "Block-C"
                l2, ln2 = base_lat + lat_off(), base_lon + lon_off()
                db.add(AccessEvent(
                    site_id=site_id, recorded_at=base_time, gate_id="G-C-Entry", 
                    zone=zone, badge_id="EXPIRED-01", outcome="fail", 
                    lat=l2, lon=ln2
                ))
                db.add(VehicleDetection(
                    site_id=site_id, recorded_at=base_time + timedelta(minutes=2),
                    zone=zone, vehicle_id=f"PL-{random.randint(100, 999)}", 
                    vehicle_type="sedan", in_restricted=True, lat=l2 + 0.0001, lon=ln2 + 0.0001
                ))
                
            elif scenario_type == "contractor_visit":
                # Successful late night maintenance
                zone = "Block-A"
                db.add(AccessEvent(
                    site_id=site_id, recorded_at=base_time, gate_id="G-A-Maint", 
                    zone=zone, badge_id="CONT-99", outcome="success", 
                    lat=base_lat + lat_off(), lon=base_lon + lon_off()
                ))
            
            # Always add some weather context
            db.add(WeatherReading(
                site_id=site_id, recorded_at=base_time, temp_c=22.5, 
                wind_kmh=random.uniform(2, 15), precipitation='none'
            ))

        db.commit()
        print("Bulk seeding complete: 50+ diverse scenarios added.")
        
    except Exception as e:
        print(f"Error during bulk seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    bulk_seed()
