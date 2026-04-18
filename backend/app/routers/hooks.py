from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.hook_events import HookEvent
from ..models.investigation_runs import InvestigationRun
from ..agent.orchestrator import investigate_cluster
from ..config import settings
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import asyncio

router = APIRouter(prefix="/hooks", tags=["hooks"])

class ObservationHook(BaseModel):
    observer: str
    zone_id: str
    observation: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    severity: str = "medium"
    lookback_minutes: int = 120

@router.post("/")
async def submit_observation(
    hook: ObservationHook, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """
    Manually trigger an investigation based on a human observation.
    """
    # 1. Record the hook
    hook_record = HookEvent(
        site_id=settings.SITE_ID,
        submitted_by=hook.observer,
        observation=hook.observation,
        zone=hook.zone_id,
        lat=hook.lat,
        lon=hook.lon,
        severity_hint=hook.severity,
        lookback_minutes=hook.lookback_minutes
    )
    db.add(hook_record)
    db.flush()
    
    # 2. Create an Investigation Run
    run = InvestigationRun(
        site_id=settings.SITE_ID,
        trigger_type="incident_hook",
        trigger_source=str(hook_record.id),
        status="running",
        window_end=datetime.utcnow(),
        window_start=datetime.utcnow() - timedelta(minutes=hook.lookback_minutes)
    )
    db.add(run)
    db.flush()
    
    hook_record.run_id = run.id
    db.commit()
    
    # 3. Queue the targeted drone/scan
    background_tasks.add_task(run_targeted_investigation, run.id, hook_record.id)
    
    return {"status": "queued", "run_id": str(run.id), "hook_id": str(hook_record.id)}

async def run_targeted_investigation(run_id: uuid.UUID, hook_id: uuid.UUID):
    # This would re-instantiate the orchestrator with target-specific focus
    # For MVP, we'll implement this when we refine the orchestrator for targeted tasks
    print(f" Maya starting targeted investigation for hook {hook_id}")
    pass
