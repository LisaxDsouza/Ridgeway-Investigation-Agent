from sqlalchemy.orm import Session
from datetime import datetime
from collections import defaultdict
from ..models.vehicle_detections import VehicleDetection

class VehicleService:
    def __init__(self, db: Session):
        self.db = db

    def get_for_window(
        self,
        site_id: str,
        start: datetime,
        end: datetime,
        zone: str = None,
        restricted_only: bool = False
    ) -> dict:
        query = self.db.query(VehicleDetection).filter(
            VehicleDetection.site_id == site_id,
            VehicleDetection.recorded_at >= start,
            VehicleDetection.recorded_at <= end
        )

        if zone:
            query = query.filter(VehicleDetection.zone == zone)
        if restricted_only:
            query = query.filter(VehicleDetection.in_restricted == True)

        events = query.order_by(VehicleDetection.recorded_at.asc()).all()

        # Group by path_segment_id for reconstruction
        paths = defaultdict(list)
        for e in events:
            if e.path_segment_id:
                paths[e.path_segment_id].append(e)

        path_segments = []
        for pid, points in paths.items():
            path_segments.append({
                "path_segment_id": pid,
                "vehicle_id": points[0].vehicle_id,
                "start_time": points[0].recorded_at.isoformat(),
                "end_time": points[-1].recorded_at.isoformat(),
                "points": [
                    {
                        "lat": float(pt.lat),
                        "lon": float(pt.lon),
                        "recorded_at": pt.recorded_at.isoformat(),
                        "speed_kmh": float(pt.speed_kmh) if pt.speed_kmh else 0
                    } for pt in points
                ],
                "entered_restricted": any(pt.in_restricted for pt in points),
                "zones_traversed": list(set(pt.zone for pt in points))
            })

        return {
            "available": len(events) > 0,
            "count": len(events),
            "restricted_zone_count": sum(1 for e in events if e.in_restricted),
            "unique_vehicles": len(set(e.vehicle_id for e in events if e.vehicle_id)),
            "events": [
                {
                    "id": str(e.id),
                    "recorded_at": e.recorded_at.isoformat(),
                    "vehicle_id": e.vehicle_id,
                    "in_restricted": e.in_restricted,
                    "zone": e.zone
                } for e in events
            ],
            "path_segments": path_segments
        }
