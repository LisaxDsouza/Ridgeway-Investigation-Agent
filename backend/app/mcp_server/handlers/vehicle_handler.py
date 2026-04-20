import sqlite3
import os
from ...agent.evidence_schema import normalize_list
from ..utils import get_data_source_path

async def handle(site_id, start_time, end_time, zone, restricted_only):
    try:
        db_path = get_data_source_path('vehicle_logs.db')
        if not os.path.exists(db_path):
            return {"error": "Vehicle log database not found."}
            
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM vehicles WHERE site_id = ?"
        params = [site_id]
        
        if zone:
            query += " AND zone = ?"
            params.append(zone)
        if restricted_only:
            query += " AND is_restricted = 1"
            
        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "source": "Vendor Tracking (SQLite)",
            "format": "SQLite",
            "data": normalize_list(rows, "Vendor Tracking System", "sqlite")
        }
    except Exception as e:
        return {"available": False, "error": str(e)}

