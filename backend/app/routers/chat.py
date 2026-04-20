from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
import groq
from ..config import settings
from .investigate import start_investigation
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(prefix="/chat", tags=["chat"])
client = groq.AsyncGroq(api_key=settings.GROQ_API_KEY)

class ChatRequest(BaseModel):
    message: str

@router.post("/")
async def maya_general_chat(
    request: ChatRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Global Maya chat. Can trigger autonomous investigations or answer site questions.
    """
    msg = request.message.lower()
    
    # 1. Check for autonomous triggers
    if any(k in msg for k in ['investigate', 'scan', 'start', 'breach', 'anomaly']):
        # Trigger investigation in background
        background_tasks.add_task(start_investigation, background_tasks, db)
        return {
            "answer": "**SCAN IN PROGRESS.** Cross-referencing source telemetry now. Results will appear in the dashboard momentarily.",
            "action": "trigger_scan"
        }
    
    # 2. Data Retrieval for RAG (Retrieval Augmented Generation)
    from ..models import SensorReading, AccessEvent, VehicleDetection
    from datetime import datetime
    
    # Fetch most recent telemetry
    sensors = db.query(SensorReading).order_by(SensorReading.recorded_at.desc()).limit(20).all()
    access = db.query(AccessEvent).order_by(AccessEvent.recorded_at.desc()).limit(20).all()
    vehicles = db.query(VehicleDetection).order_by(VehicleDetection.recorded_at.desc()).limit(20).all()
    
    context = "RECENT FORENSIC LOGS:\n"
    for s in sensors: context += f"[{s.recorded_at}] SENSOR: {s.sensor_type} @ {s.zone} (Value: {s.raw_value})\n"
    for a in access: context += f"[{a.recorded_at}] ACCESS: {a.outcome} for {a.badge_id} @ {a.gate_id}\n"
    for v in vehicles: context += f"[{v.recorded_at}] VEHICLE: {v.vehicle_type} {v.vehicle_id} @ {v.zone} (Restricted: {v.in_restricted})\n"

    curr_time = datetime.utcnow().isoformat()
    
    # 3. General Query Handling
    try:
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": f"""You are the Ridgeway Forensic AI. 
                    Current System Time: {curr_time}
                    
                    {context}
                    
                    Answer questions DIRECTLY based on the logs provided above. 
                    Do NOT describe your internal modules or thought process.
                    ONLY provide findings and data analysis.
                    If asked about time-relative events (e.g. 'last 1 hour'), calculate based on the Current System Time and the log timestamps."""
                },
                {"role": "user", "content": request.message}
            ]
        )
        return {"answer": response.choices[0].message.content, "action": "none"}
    except groq.RateLimitError:
        # Fallback to smaller model if primary fails
        try:
            fallback_model = "llama-3.1-8b-instant"
            if settings.GROQ_MODEL == fallback_model:
                raise # Already using fallback, re-raise
                
            response = await client.chat.completions.create(
                model=fallback_model,
                messages=[
                    {"role": "system", "content": "You are Maya, the Ridgeway Forensic AI. Be concise. The primary analysis engine is under heavy load, using secondary processing."},
                    {"role": "user", "content": request.message}
                ]
            )
            return {"answer": f"(SECONDARY ENGINE) {response.choices[0].message.content}", "action": "none"}
        except Exception:
            return {
                "answer": "SYSTEM OVERLOAD. Groq rate limit reached. Please try again in a few minutes.",
                "action": "error"
            }
    except Exception as e:
        return {"answer": f"ERROR: {str(e)}", "action": "error"}
