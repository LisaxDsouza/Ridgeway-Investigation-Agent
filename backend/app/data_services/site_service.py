from sqlalchemy.orm import Session
from datetime import datetime
from ..models.site_metadata import SiteZone, ShiftSchedule

class SiteService:
    def __init__(self, db: Session):
        self.db = db

    def get_zone(self, site_id: str, zone_id: str = None) -> dict:
        query = self.db.query(SiteZone).filter(SiteZone.site_id == site_id)
        if zone_id:
            query = query.filter(SiteZone.zone_id == zone_id)
        
        zones = query.all()
        return {
            "available": len(zones) > 0,
            "zones": [
                {
                    "zone_id": z.zone_id,
                    "zone_name": z.zone_name,
                    "zone_type": z.zone_type,
                    "is_restricted": z.is_restricted,
                    "access_rules": z.access_rules,
                    "expected_vehicles": z.expected_vehicles,
                    "boundary_geojson": z.boundary_geojson
                } for z in zones
            ]
        }

    def get_shift(self, site_id: str, date_str: str) -> dict:
        # date_str in ISO format
        query = self.db.query(ShiftSchedule).filter(ShiftSchedule.site_id == site_id)
        shift = query.first() # Simplification: get first available shift for demo

        if not shift:
            return {"available": False}

        return {
            "available": True,
            "shift_type": shift.shift_type,
            "shift_start": shift.shift_start.isoformat(),
            "shift_end": shift.shift_end.isoformat(),
            "supervisor_id": shift.supervisor_id,
            "headcount": shift.headcount,
            "active_zones": shift.active_zones,
            "scheduled_maintenance": shift.scheduled_maintenance,
            "is_overnight": shift.shift_type == "night",
            "reduced_staffing": shift.headcount < 5 # Heuristic
        }
