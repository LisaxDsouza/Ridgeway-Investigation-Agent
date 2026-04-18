from ...database import SessionLocal
from ...data_services.historical_service import HistoricalService

async def handle(site_id, event_type, zone, lookback_days):
    try:
        with SessionLocal() as db:
            return HistoricalService(db).get_patterns(site_id, event_type, zone, lookback_days)
    except Exception as e:
        return {"available": False, "error": str(e)}
