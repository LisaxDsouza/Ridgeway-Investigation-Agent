from datetime import datetime
from ...database import SessionLocal
from ...data_services.vehicle_service import VehicleService

async def handle(site_id, start_time, end_time, zone, restricted_only):
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        with SessionLocal() as db:
            return VehicleService(db).get_for_window(
                site_id, start, end, zone, restricted_only
            )
    except Exception as e:
        return {"available": False, "error": str(e)}
