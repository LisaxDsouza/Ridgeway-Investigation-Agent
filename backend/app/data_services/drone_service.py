from sqlalchemy.orm import Session
from datetime import datetime
from collections import defaultdict
from ..models.drone_telemetry import DroneTelemetry

class DroneService:
    def __init__(self, db: Session):
        self.db = db

    def get_for_window(
        self,
        site_id: str,
        mission_id: str = None,
        start: datetime = None,
        end: datetime = None,
        flagged_only: bool = False
    ) -> dict:
        query = self.db.query(DroneTelemetry).filter(DroneTelemetry.site_id == site_id)

        if mission_id:
            query = query.filter(DroneTelemetry.mission_id == mission_id)
        if start:
            query = query.filter(DroneTelemetry.recorded_at >= start)
        if end:
            query = query.filter(DroneTelemetry.recorded_at <= end)
        if flagged_only:
            query = query.filter(DroneTelemetry.flagged == True)

        readings = query.order_by(DroneTelemetry.recorded_at.asc()).all()

        # Group by mission_id
        missions_map = defaultdict(list)
        for r in readings:
            missions_map[r.mission_id].append(r)

        missions = []
        for mid, pts in missions_map.items():
            missions.append({
                "mission_id": mid,
                "mission_type": pts[0].mission_type,
                "drone_id": pts[0].drone_id,
                "start_time": pts[0].recorded_at.isoformat(),
                "end_time": pts[-1].recorded_at.isoformat(),
                "waypoint_count": len(pts),
                "flagged_count": sum(1 for pt in pts if pt.flagged),
                "path_geojson": {
                    "type": "LineString",
                    "coordinates": [[float(pt.lon), float(pt.lat)] for pt in pts]
                },
                "waypoints": [
                    {
                        "index": pt.waypoint_index,
                        "lat": float(pt.lat),
                        "lon": float(pt.lon),
                        "recorded_at": pt.recorded_at.isoformat(),
                        "observation": pt.observation,
                        "flagged": pt.flagged,
                        "flag_reason": pt.flag_reason
                    } for pt in pts
                ]
            })

        return {
            "available": len(missions) > 0,
            "missions": missions
        }
