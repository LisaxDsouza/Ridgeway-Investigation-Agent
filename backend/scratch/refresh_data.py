import json
import os
import sqlite3
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load env before importing settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

DATA_DIR = os.path.join(BASE_DIR, 'data_sources')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Current time for mock data (around the user's current time)
now = datetime(2026, 4, 20, 18, 0, 0)

# ... (JSON/SQLite seeding logic same as before) ...

# 1. Weather JSON
weather_data = [
    {
        "site_id": "ridgeway-01",
        "timestamp": (now - timedelta(hours=1)).isoformat() + "Z",
        "type": "weather",
        "wind_speed": 15.0,
        "visibility": 1000,
        "precipitation": 0.0,
        "raw_value": "WIND: 15km/h, VIS: 1000m"
    },
    {
        "site_id": "ridgeway-01",
        "timestamp": (now - timedelta(hours=3)).isoformat() + "Z",
        "type": "weather",
        "wind_speed": 48.5,
        "visibility": 150,
        "precipitation": 12.0,
        "raw_value": "WIND: 48.5km/h, VIS: 150m (SEVERE STORM)"
    }
]
with open(os.path.join(DATA_DIR, 'weather_api.json'), 'w') as f:
    json.dump(weather_data, f, indent=4)

# 2. Drone JSON
drone_data = [
    {
        "mission_id": "mission-99",
        "timestamp": (now - timedelta(minutes=45)).isoformat() + "Z",
        "lat": 13.0485,
        "lon": 77.5435,
        "observation": "High heat signature detected near perimeter fence block A.",
        "confidence": 0.89,
        "type": "drone_observation"
    }
]
with open(os.path.join(DATA_DIR, 'drone_logs.json'), 'w') as f:
    json.dump(drone_data, f, indent=4)

# 3. SQLite Dbs
def init_sqlite():
    conn = sqlite3.connect(os.path.join(DATA_DIR, 'vehicle_logs.db'))
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS vehicles')
    c.execute('CREATE TABLE vehicles (id INTEGER PRIMARY KEY, vehicle_id TEXT, site_id TEXT, zone TEXT, timestamp TEXT, lat REAL, lon REAL, is_restricted BOOLEAN)')
    c.execute("INSERT INTO vehicles (vehicle_id, site_id, zone, timestamp, lat, lon, is_restricted) VALUES ('KA-12-X-4567', 'ridgeway-01', 'HMT-Loading', ?, 13.0480, 77.5430, 1)", ((now - timedelta(hours=2)).isoformat() + "Z",))
    conn.commit()
    conn.close()

    conn = sqlite3.connect(os.path.join(DATA_DIR, 'badge_logs.db'))
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS badges')
    c.execute('CREATE TABLE badges (id INTEGER PRIMARY KEY, badge_id TEXT, site_id TEXT, gate_id TEXT, timestamp TEXT, outcome TEXT)')
    c.execute("INSERT INTO badges (badge_id, site_id, gate_id, timestamp, outcome) VALUES ('staff-88', 'ridgeway-01', 'HMT-Main', ?, 'success')", ((now - timedelta(minutes=15)).isoformat() + "Z",))
    conn.commit()
    conn.close()

init_sqlite()

# 4. CSV Shift
with open(os.path.join(DATA_DIR, 'shift_schedule.csv'), 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['date', 'site_id', 'staff_id', 'role', 'zone', 'shift_start', 'shift_end'])
    writer.writerow(['2026-04-20', 'ridgeway-01', 'staff-88', 'Security', 'Global', '08:00:00', '20:00:00'])

# 5. PostgreSQL Seed (Triggers)
import sys
sys.path.append(BASE_DIR)
try:
    from app.database import SessionLocal
    from app.models import SensorReading, AccessEvent
    from app.models.site_metadata import SiteZone
    db = SessionLocal()
    site_id = "ridgeway-01"
    
    # 0. Flush and Seed Site Metadata (Layout)
    db.query(SiteZone).delete()
    db.add_all([
        SiteZone(site_id=site_id, zone_id="block-a", zone_name="Logistics Center", zone_type="workzone", is_restricted=False, expected_vehicles=True),
        SiteZone(site_id=site_id, zone_id="block-b", zone_name="Parts Warehouse", zone_type="storage", is_restricted=False, expected_vehicles=False),
        SiteZone(site_id=site_id, zone_id="block-c", zone_name="Precision Manufacturing", zone_type="restricted", is_restricted=True, expected_vehicles=False),
    ])

    # 1. High-severity Sensor Breach
    db.add(SensorReading(
        site_id=site_id,
        recorded_at=now - timedelta(minutes=10),
        sensor_id="SN-NORTH-01",
        sensor_type="vibration",
        zone="block-c", # Moved to restricted zone for better reasoning
        raw_value=0.95,
        threshold=0.5,
        threshold_breached=True,
        lat=13.0485,
        lon=77.5435
    ))

    # 2. Access Failure
    db.add(AccessEvent(
        site_id=site_id,
        recorded_at=now - timedelta(minutes=5),
        gate_id="G-STAFF-02",
        zone="HMT-Entry",
        badge_id="BAD-ID-X99",
        outcome="fail",
        lat=13.0486,
        lon=77.5436
    ))

    db.commit()
    db.close()
    print("Main DB Triggers seeded successfully.")
except Exception as e:
    print(f"PostgreSQL seeding failed: {e}")

print("Fresh mock data for 2026-04-20 generated successfully.")
