import os
import sys
from sqlalchemy.orm import Session

# Add the parent directory to sys.path to allow imports from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import Incident, InvestigationRun, SensorReading, AccessEvent, VehicleDetection, DroneTelemetry

def clear_db():
    print("Clearing forensic data...")
    db = SessionLocal()
    try:
        # Clear all investigation data
        db.query(Incident).delete()
        db.query(InvestigationRun).delete()
        
        # Optionally unlink readings or clear them if they are "simulated"
        # For a hard reset, let's just clear everything so the user can start fresh
        db.query(SensorReading).delete()
        db.query(AccessEvent).delete()
        db.query(VehicleDetection).delete()
        db.query(DroneTelemetry).delete()
        
        db.commit()
        print("Investigations and signals cleared successfully.")
        
    except Exception as e:
        print(f"Error clearing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_db()
