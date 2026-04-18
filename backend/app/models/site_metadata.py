from sqlalchemy import Column, String, Numeric, Boolean, DateTime, Date, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from uuid import uuid4
from datetime import datetime
from ..database import Base

class SiteZone(Base):
    __tablename__ = "site_zones"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    site_id             = Column(String(64), nullable=False)
    zone_id             = Column(String(128), nullable=False, unique=True)
    zone_name           = Column(String(256))
    zone_type           = Column(String(64))
    # zone_type values: perimeter | storage | workzone | access | restricted
    is_restricted       = Column(Boolean, nullable=False, default=False)
    access_rules        = Column(JSONB, default={})
    # access_rules shape: { allowed_roles, allowed_hours, requires_escort }
    boundary_geojson    = Column(JSONB)
    expected_vehicles   = Column(Boolean, default=False)
    notes               = Column(Text)


class ShiftSchedule(Base):
    __tablename__ = "shift_schedule"

    id                      = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    site_id                 = Column(String(64), nullable=False)
    shift_date              = Column(Date, nullable=False)
    shift_type              = Column(String(32), nullable=False)
    # shift_type values: day | night | weekend
    shift_start             = Column(DateTime(timezone=True), nullable=False)
    shift_end               = Column(DateTime(timezone=True), nullable=False)
    supervisor_id           = Column(String(128))
    headcount               = Column(Integer)
    active_zones            = Column(JSONB, default=[])
    scheduled_maintenance   = Column(JSONB, default=[])
