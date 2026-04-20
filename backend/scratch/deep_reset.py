import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Load env before importing settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Add parent to sys.path to import app
sys.path.append(os.path.dirname(BASE_DIR))

from app.database import SessionLocal
from app.models import (
    SensorReading, AccessEvent, VehicleDetection, DroneTelemetry,
    Incident, InvestigationRun
)
from app.models.briefing import Briefing

def deep_reset():
    print("--- [FORENSIC DEEP RESET] ---")
    db = SessionLocal()
    try:
        # Delete data in order to respect any foreign keys if we had them
        print("[*] Clearing Briefings...")
        db.query(Briefing).delete()
        
        print("[*] Clearing Incidents & Runs...")
        db.query(InvestigationRun).delete()
        db.query(Incident).delete()
        
        print("[*] Clearing Forensic Signals (PostgreSQL)...")
        db.query(SensorReading).delete()
        db.query(AccessEvent).delete()
        db.query(VehicleDetection).delete()
        db.query(DroneTelemetry).delete()
        
        db.commit()
        print("[SUCCESS] Forensic Intelligence Pool has been wiped clean.")
        
    except Exception as e:
        db.rollback()
        print(f"[FAILED] Reset failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    deep_reset()
