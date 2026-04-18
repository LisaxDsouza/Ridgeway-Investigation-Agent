from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Incident

from pydantic import BaseModel
import groq
from ..config import settings

router = APIRouter(prefix="/incidents", tags=["incidents"])

client = groq.Groq(api_key=settings.GROQ_API_KEY)

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
def chat_with_incident(incident_id: str, request: ChatRequest, db: Session = Depends(get_db)):
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
    
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are the Ridgeway Site Assistant. Answer questions about this specific incident log based on the provided context."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {request.message}"}
        ]
    )
    
    return {"answer": response.choices[0].message.content}
