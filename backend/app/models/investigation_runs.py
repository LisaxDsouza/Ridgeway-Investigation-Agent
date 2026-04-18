from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime
from ..database import Base

class InvestigationRun(Base):
    __tablename__ = "investigation_runs"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at          = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at        = Column(DateTime(timezone=True))
    site_id             = Column(String(64), nullable=False)
    trigger_type        = Column(String(64), nullable=False)
    # trigger_type values: scheduled | incident_hook | manual
    trigger_source      = Column(String(128))
    # trigger_source: hook_id if incident_hook, "cron" if scheduled
    status              = Column(String(32), nullable=False, default="queued")
    # status values: queued | running | complete | failed
    window_start        = Column(DateTime(timezone=True), nullable=False)
    window_end          = Column(DateTime(timezone=True), nullable=False)
    events_fetched      = Column(Integer, default=0)
    clusters_found      = Column(Integer, default=0)
    incidents_created   = Column(Integer, default=0)
    error_message       = Column(Text)
