from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Event, Incident
from ..agent.orchestrator import investigate_cluster
from ..tools.spatial_tools import cluster_events_by_location
import uuid

router = APIRouter(prefix="/investigate", tags=["investigation"])

# Simple in-memory status tracker for MVP
jobs = {}

@router.post("/")
async def start_investigation(background_tasks: background_tasks, db: Session = Depends(get_db)):
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

def run_investigation_job(job_id: str, db: Session):
    try:
        # 1. Fetch all events (in production, filter by 'overnight' window)
        events = db.query(Event).all()
        event_dicts = [e.__dict__ for e in events]
        
        # 2. Cluster events
        clusters = cluster_events_by_location(event_dicts)
        
        # 3. Investigate each cluster
        for cluster in clusters:
            # Re-fetch event objects to ensure session compatibility
            event_ids = [e['id'] for e in cluster]
            event_objs = db.query(Event).filter(Event.id.in_(event_ids)).all()
            
            investigate_cluster(event_objs, db)
        
        jobs[job_id] = "complete"
    except Exception as e:
        print(f"Investigation job failed: {e}")
        jobs[job_id] = "failed"
