from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.briefing import Briefing
from ..services.briefing_service import BriefingService
from ..config import settings
from datetime import datetime

router = APIRouter(prefix="/briefings", tags=["briefings"])

@router.get("/")
def list_briefings(db: Session = Depends(get_db)):
    return db.query(Briefing).order_by(Briefing.created_at.desc()).all()

@router.post("/generate")
async def generate_briefing(db: Session = Depends(get_db)):
    service = BriefingService(db)
    briefing = await service.generate_morning_brief(settings.SITE_ID)
    if not briefing:
        return {"message": "No incidents found to summarize."}
    return briefing
