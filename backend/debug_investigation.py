from app.database import SessionLocal
from app.models import Event
from app.agent.orchestrator import investigate_cluster

db = SessionLocal()
try:
    events = db.query(Event).all()
    print(f"Found {len(events)} events.")
    result = investigate_cluster(events, db)
    print("Investigation complete.")
    print(result)
except Exception as e:
    print(f"FAILED: {e}")
finally:
    db.close()
