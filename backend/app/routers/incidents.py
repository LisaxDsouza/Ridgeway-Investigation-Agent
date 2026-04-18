from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Incident

router = APIRouter(prefix="/incidents", tags=["incidents"])

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
