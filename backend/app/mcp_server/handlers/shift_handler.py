from ...database import SessionLocal
from ...data_services.site_service import SiteService

async def handle(site_id, date):
    try:
        with SessionLocal() as db:
            return SiteService(db).get_shift(site_id, date)
    except Exception as e:
        return {"available": False, "error": str(e)}
