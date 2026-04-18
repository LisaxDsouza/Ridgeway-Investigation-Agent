import os
import sys
from sqlalchemy.orm import Session
from datetime import datetime

# Add the parent directory to sys.path to allow imports from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.config import settings
from seed.scenarios.three_block_forensics import seed_three_block_scenario
from app.models.sensor_readings import SensorReading

def seed_db():
    print("Initializing forensic database...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if already seeded (by checking sensor_readings)
        if db.query(SensorReading).count() > 0:
            print("Database already contains data. Skipping seed.")
            return

        site_id = settings.SITE_ID
        print(f"Injecting 3-Block Scenario into {site_id}...")
        seed_three_block_scenario(db, site_id)
        print("Seeding complete.")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
