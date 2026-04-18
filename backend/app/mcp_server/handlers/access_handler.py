from datetime import datetime
from ...database import SessionLocal
from ...data_services.access_service import AccessService

async def handle(site_id, start_time, end_time, gate_id, outcome_filter):
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        with SessionLocal() as db:
            return AccessService(db).get_for_window(
                site_id, start, end, gate_id, outcome_filter
            )
    except Exception as e:
        return {"available": False, "error": str(e)}
