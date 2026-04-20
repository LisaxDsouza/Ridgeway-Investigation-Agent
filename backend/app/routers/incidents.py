from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Incident

from pydantic import BaseModel
import groq
from ..config import settings

router = APIRouter(prefix="/incidents", tags=["incidents"])

client = groq.AsyncGroq(api_key=settings.GROQ_API_KEY)

class ChatRequest(BaseModel):
    message: str

@router.get("/")
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).all()

@router.get("/{incident_id}")
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.patch("/{incident_id}/review")
def review_incident(incident_id: str, update_data: dict, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    for key, value in update_data.items():
        setattr(incident, key, value)
    
    db.commit()
    db.refresh(incident)
    return incident

@router.post("/{incident_id}/chat")
async def chat_with_incident(incident_id: str, request: ChatRequest, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Construct context from incident
    context = f"""
    Incident Hypothesis: {incident.hypothesis}
    Confidence: {incident.confidence_score}
    Rationale: {incident.confidence_rationale}
    Reasoning Trace: {incident.reasoning_trace}
    """
    
    try:
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": """You are the Ridgeway Site Intelligence Officer. 
                Your goal is to provide concise, direct, and non-technical answers to the operator. 
                
                STRICT RULES:
                - NEVER mention tool names (e.g., 'getShiftSchedule', 'getWeatherContext').
                - NEVER mention 'steps' or 'reasoning traces'.
                - NEVER explain HOW you got the information. 
                - Simply state the findings as ground truth.
                - If the operator asks about staff, provide the role or name without citing the 'CSV' source.
                - Keep answers to 1-2 sentences unless complexity is truly required.
                """},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {request.message}"}
            ]
        )
        return {"answer": response.choices[0].message.content}
    except groq.RateLimitError:
        try:
            fallback_model = "llama-3.1-8b-instant"
            if settings.GROQ_MODEL == fallback_model: raise
            response = await client.chat.completions.create(
                model=fallback_model,
                messages=[
                    {"role": "system", "content": "You are the Ridgeway Site Intelligence Officer. Provide direct, non-technical answers ONLY. No tool citations. No workflow mentions."},
                    {"role": "user", "content": f"Context: {context}\n\nQuestion: {request.message}"}
                ]
            )
            return {"answer": f"(SECONDARY ENGINE) {response.choices[0].message.content}"}
        except Exception:
            return {"answer": "SYSTEM OVERLOAD: Rate limit reached. Try again later."}
    except Exception as e:
        return {"answer": f"ERROR: {str(e)}"}
