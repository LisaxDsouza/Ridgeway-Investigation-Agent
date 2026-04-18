from sqlalchemy.orm import Session
from datetime import datetime
from ..models.sensor_readings import SensorReading

class SensorService:
    def __init__(self, db: Session):
        self.db = db

    def get_for_window(
        self,
        site_id: str,
        start: datetime,
        end: datetime,
        zone: str = None,
        sensor_type: str = None,
        breached_only: bool = False
    ) -> dict:
        query = self.db.query(SensorReading).filter(
            SensorReading.site_id == site_id,
            SensorReading.recorded_at >= start,
            SensorReading.recorded_at <= end
        )

        if zone:
            query = query.filter(SensorReading.zone == zone)
        if sensor_type:
            query = query.filter(SensorReading.sensor_type == sensor_type)
        if breached_only:
            query = query.filter(SensorReading.threshold_breached == True)

        readings = query.order_by(SensorReading.recorded_at.asc()).all()
        
        return {
            "available": len(readings) > 0,
            "count": len(readings),
            "events": [
                {
                    "id": str(r.id),
                    "recorded_at": r.recorded_at.isoformat(),
                    "zone": r.zone,
                    "sensor_type": r.sensor_type,
                    "raw_value": float(r.raw_value) if r.raw_value else None,
                    "threshold_breached": r.threshold_breached,
                    "lat": float(r.lat) if r.lat else None,
                    "lon": float(r.lon) if r.lon else None
                } for r in readings
            ],
            "breached_count": sum(1 for r in readings if r.threshold_breached),
            "zones_affected": list(set(r.zone for r in readings))
        }

    def get_by_ids(self, ids: list[str]) -> dict:
        readings = self.db.query(SensorReading).filter(SensorReading.id.in_(ids)).all()
        return {
            "count": len(readings),
            "events": [
                {
                    "id": str(r.id),
                    "recorded_at": r.recorded_at.isoformat(),
                    "sensor_type": r.sensor_type,
                    "zone": r.zone
                } for r in readings
            ]
        }
