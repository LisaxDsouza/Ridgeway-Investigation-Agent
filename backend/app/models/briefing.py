from sqlalchemy import Column, String, DateTime, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime
from ..database import Base

class Briefing(Base):
    __tablename__ = "briefings"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at      = Column(DateTime(timezone=True), default=datetime.utcnow)
    briefing_date   = Column(Date, nullable=False, default=datetime.utcnow().date())
    site_id         = Column(String(64), nullable=False)
    
    # Q1: what actually happened last night
    q1_summary      = Column(Text)
    # Q2: what was harmless
    q2_harmless     = Column(Text)
    # Q3: what deserves escalation
    q3_escalations  = Column(Text)
    # Q4: what did the drone check
    q4_drone_ops    = Column(Text)
    # Q5: what still needs follow-up
    q5_follow_ups   = Column(Text)
    
    export_text     = Column(Text)
