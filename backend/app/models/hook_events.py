from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import uuid4
from datetime import datetime
from ..database import Base

class HookEvent(Base):
    __tablename__ = "hook_events"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at          = Column(DateTime(timezone=True), default=datetime.utcnow)
    site_id             = Column(String(64), nullable=False)
    submitted_by        = Column(String(128), nullable=False)
    observation         = Column(Text, nullable=False)
    zone                = Column(String(64))
    lat                 = Column(Numeric(10, 7))
    lon                 = Column(Numeric(10, 7))
    severity_hint       = Column(String(16))
    # severity_hint values: low | medium | high
    lookback_minutes    = Column(Integer, nullable=False, default=120)
    include_sources     = Column(JSONB, default=["sensor","vehicle","access","drone","weather"])
    notes               = Column(Text)
    status              = Column(String(32), nullable=False, default="queued")
    # status values: queued | processing | complete | failed
    run_id              = Column(UUID(as_uuid=True), ForeignKey("investigation_runs.id"))
    incident_id         = Column(UUID(as_uuid=True), ForeignKey("incidents.id"))
    error_message       = Column(Text)
