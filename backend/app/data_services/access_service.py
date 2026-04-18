from sqlalchemy.orm import Session
from datetime import datetime
from ..models.access_events import AccessEvent

class AccessService:
    def __init__(self, db: Session):
        self.db = db

    def get_for_window(
        self,
        site_id: str,
        start: datetime,
        end: datetime,
        gate_id: str = None,
        outcome_filter: str = None
    ) -> dict:
        query = self.db.query(AccessEvent).filter(
            AccessEvent.site_id == site_id,
            AccessEvent.recorded_at >= start,
            AccessEvent.recorded_at <= end
        )

        if gate_id:
            query = query.filter(AccessEvent.gate_id == gate_id)
        if outcome_filter:
            query = query.filter(AccessEvent.outcome == outcome_filter)

        events = query.order_by(AccessEvent.recorded_at.asc()).all()

        # Calculate max consecutive failures for the same gate (heuristic for brute force)
        max_consecutive = 0
        current_consecutive = 0
        last_gate = None
        for e in events:
            if e.outcome != 'success':
                if e.gate_id == last_gate:
                    current_consecutive += 1
                else:
                    current_consecutive = 1
                    last_gate = e.gate_id
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
                last_gate = None

        return {
            "available": len(events) > 0,
            "count": len(events),
            "failed_count": sum(1 for e in events if e.outcome != 'success'),
            "events": [
                {
                    "id": str(e.id),
                    "recorded_at": e.recorded_at.isoformat(),
                    "gate_id": e.gate_id,
                    "zone": e.zone,
                    "badge_id": e.badge_id,
                    "outcome": e.outcome,
                    "failure_reason": e.failure_reason,
                    "lat": float(e.lat) if e.lat else None,
                    "lon": float(e.lon) if e.lon else None
                } for e in events
            ],
            "gates_with_failures": list(set(e.gate_id for e in events if e.outcome != 'success')),
            "consecutive_failures": max_consecutive
        }
