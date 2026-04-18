from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Incident, InvestigationRun
from ..tools.spatial_tools import cluster_events_by_location
import uuid

router = APIRouter(prefix="/investigate", tags=["investigation"])

# Simple in-memory status tracker for MVP
jobs = {}

@router.post("/")
async def start_investigation(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Trigger full agent investigation run.
    """
    job_id = str(uuid.uuid4())
    jobs[job_id] = "running"
    
    background_tasks.add_task(run_investigation_job, job_id, db)
    
    return {"job_id": job_id, "status": "running"}

@router.get("/{job_id}/status")
async def get_status(job_id: str):
    return {"status": jobs.get(job_id, "unknown")}

from datetime import datetime, timedelta
from ..agent.orchestrator import investigate_cluster
from ..models import SensorReading, AccessEvent, VehicleDetection, DroneTelemetry
from ..config import settings
import asyncio

def run_investigation_job(job_id: str, db: Session):
    try:
        site_id = settings.SITE_ID
        # 1. Look back 24 hours for unassigned signals
        window_start = datetime.utcnow() - timedelta(hours=24)
        
        # 2. Gather primary "Trigger" signals that aren't yet linked to an incident
        # Priority: Sensor breaches, Failed Access, Restricted Vehicles, Flagged Drone readings
        
        triggers = []
        
        # Sensor breaches
        sensors = db.query(SensorReading).filter(
            SensorReading.site_id == site_id,
            SensorReading.recorded_at >= window_start,
            SensorReading.incident_id == None,
            SensorReading.threshold_breached == True
        ).all()
        triggers.extend([{"type": "sensor", "id": str(s.id), "lat": float(s.lat), "lon": float(s.lon), "recorded_at": s.recorded_at.isoformat()} for s in sensors])
        
        # Failed Access
        access = db.query(AccessEvent).filter(
            AccessEvent.site_id == site_id,
            AccessEvent.recorded_at >= window_start,
            AccessEvent.incident_id == None,
            AccessEvent.outcome == "fail"
        ).all()
        triggers.extend([{"type": "access", "id": str(a.id), "lat": float(a.lat), "lon": float(a.lon), "recorded_at": a.recorded_at.isoformat()} for a in access])
        
        # Restricted Vehicles
        vehicles = db.query(VehicleDetection).filter(
            VehicleDetection.site_id == site_id,
            VehicleDetection.recorded_at >= window_start,
            VehicleDetection.incident_id == None,
            VehicleDetection.in_restricted == True
        ).all()
        triggers.extend([{"type": "vehicle", "id": str(v.id), "lat": float(v.lat), "lon": float(v.lon), "recorded_at": v.recorded_at.isoformat()} for v in vehicles])

        if not triggers:
            print("No new trigger signals found for investigation.")
            jobs[job_id] = "no_signals"
            return
            
        print(f"Maya found {len(triggers)} trigger signals. Clustering...")

        # 3. Cluster events spatially
        clusters = cluster_events_by_location(triggers)
        print(f"Formed {len(clusters)} clusters for investigation.")

        # 4. Investigate each cluster asynchronously
        for i, cluster in enumerate(clusters):
            print(f"Maya starting investigation for cluster {i} ({len(cluster)} signals)...")
            # For simplicity in this script, we run them sequentially but they use async agent loops
            asyncio.run(investigate_cluster(cluster, db, site_id))
        
        jobs[job_id] = "complete"
        
    except Exception as e:
        print(f"Investigation job failed: {e}")
        jobs[job_id] = f"failed: {str(e)}"
