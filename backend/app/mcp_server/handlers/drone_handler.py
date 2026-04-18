from datetime import datetime
from ...database import SessionLocal
from ...data_services.drone_service import DroneService

async def handle(site_id, start_time, end_time, mission_id, flagged_only):
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00')) if start_time else None
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00')) if end_time else None
        with SessionLocal() as db:
            return DroneService(db).get_for_window(
                site_id, mission_id, start, end, flagged_only
            )
    except Exception as e:
        return {"available": False, "error": str(e)}
