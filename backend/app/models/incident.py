from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import uuid4
from datetime import datetime
from ..database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id                      = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at              = Column(DateTime(timezone=True), default=datetime.utcnow)
    site_id                 = Column(String(64), nullable=False)
    
    investigation_run_id    = Column(UUID(as_uuid=True), ForeignKey("investigation_runs.id"), nullable=True)
    related_event_ids       = Column(JSONB, nullable=False, default=[])
    related_sources         = Column(JSONB, nullable=False, default=[])
    # related_sources: ["sensor", "access"] — which source tables contributed
    cluster_centroid_lat    = Column(Numeric(10, 7))
    cluster_centroid_lon    = Column(Numeric(10, 7))
    
    hypothesis              = Column(Text, nullable=False)
    confidence_score        = Column(Numeric(4, 3), nullable=False)
    # confidence_score: 0.000 to 1.000
    confidence_level        = Column(String(16), nullable=False)
    # confidence_level: low | medium | high
    confidence_rationale    = Column(Text)
    
    recommended_action      = Column(String(64), nullable=False)
    # recommended_action: none | monitor | notify_supervisor | review_footage
    
    reasoning_trace         = Column(JSONB, nullable=False, default=[])
    # reasoning_trace: full list of messages exchanged with Groq
    tool_calls_made         = Column(JSONB, nullable=False, default=[])
    # tool_calls_made: [{tool, args, result_summary}] ordered list
    
    triggered_by            = Column(String(64), default="scheduled")
    # triggered_by: scheduled | incident_hook | manual
    
    review_status           = Column(String(32), default="pending")
    # review_status: pending | accepted | dismissed | refined | challenged
    human_note              = Column(Text)
    
    original_confidence     = Column(Numeric(4, 3))
    # original_confidence: set when human overrides — preserves what agent said
