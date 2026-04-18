from sqlalchemy import Column, String, Float, JSON, Enum
from ..database import Base
import uuid
import enum

class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REFINED = "refined"
    CHALLENGED = "challenged"
    DISMISSED = "dismissed"

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    hypothesis = Column(String)
    confidence_score = Column(Float)
    confidence_rationale = Column(String)
    recommended_action = Column(String)
    reasoning_trace = Column(JSON, default=[]) # list of tool calls and insights
    review_status = Column(String, default=ReviewStatus.PENDING)
    human_note = Column(String, nullable=True)
    cluster_center_lat = Column(Float)
    cluster_center_lon = Column(Float)
