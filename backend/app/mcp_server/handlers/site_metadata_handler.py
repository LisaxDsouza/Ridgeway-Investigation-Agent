from ...database import SessionLocal
from ...data_services.site_service import SiteService

async def handle(site_id, zone_id):
    try:
        with SessionLocal() as db:
            return SiteService(db).get_zone(site_id, zone_id)
    except Exception as e:
        return {"available": False, "error": str(e)}
