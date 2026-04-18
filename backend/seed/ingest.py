import os
import sys
from sqlalchemy.orm import Session
from datetime import datetime

# Add the parent directory to sys.path to allow imports from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import Event
from seed.scenarios.block_c_incident import get_block_c_scenario

def seed_db():
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Event).count() > 0:
            print("Database already contains events. Skipping seed.")
            return

        print("Seeding Block C Scenario...")
        scenario_events = get_block_c_scenario()
        for event_data in scenario_events:
            event = Event(**event_data)
            db.add(event)
        
        db.commit()
        print(f"Successfully seeded {len(scenario_events)} events.")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
