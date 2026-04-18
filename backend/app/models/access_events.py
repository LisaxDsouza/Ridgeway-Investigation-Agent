from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import uuid4
from datetime import datetime
from ..database import Base

class AccessEvent(Base):
    __tablename__ = "access_events"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    recorded_at         = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    site_id             = Column(String(64), nullable=False)
    gate_id             = Column(String(128), nullable=False)
    zone                = Column(String(64), nullable=False)
    badge_id            = Column(String(128))
    person_id           = Column(String(128))
    outcome             = Column(String(32), nullable=False)
    # outcome values: success | fail | error | maintenance
    failure_reason      = Column(String(256))
    lat                 = Column(Numeric(10, 7))
    lon                 = Column(Numeric(10, 7))
    incident_id         = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    metadata_json       = Column(JSONB, default={})
