import sqlite3
import os
from ...agent.evidence_schema import normalize_list
from ..utils import get_data_source_path

async def handle(site_id, start_time, end_time, gate_id, outcome_filter):
    try:
        db_path = get_data_source_path('badge_logs.db')
        if not os.path.exists(db_path):
            return {"error": "Access log database not found."}
            
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM badges WHERE site_id = ?"
        params = [site_id]
        
        if gate_id:
            query += " AND gate_id = ?"
            params.append(gate_id)
        if outcome_filter:
            query += " AND outcome = ?"
            params.append(outcome_filter)
            
        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "source": "Access Control (SQLite)",
            "format": "SQLite",
            "data": normalize_list(rows, "Access Control System", "sqlite")
        }
    except Exception as e:
        return {"available": False, "error": str(e)}

