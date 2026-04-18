from sqlalchemy import Column, String, DateTime, Text, Date
from sqlalchemy.sql import func
from ..database import Base
import uuid

class Briefing(Base):
    __tablename__ = "briefings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(Date, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # The five questions for Nisha
    q1_summary = Column(Text) # What actually happened last night?
    q2_harmless = Column(Text) # What was harmless?
    q3_escalations = Column(Text) # What deserves escalation?
    q4_drone_work = Column(Text) # What did the drone check?
    q5_followups = Column(Text) # What still needs follow-up?
    
    export_text = Column(Text, nullable=True) # Formatted text for final handoff
