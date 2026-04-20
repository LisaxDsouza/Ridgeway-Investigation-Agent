import csv
import os
from datetime import datetime
from ...agent.evidence_schema import normalize_list
from ..utils import get_data_source_path

async def handle(site_id, date):
    try:
        data_path = get_data_source_path('shift_schedule.csv')
        if not os.path.exists(data_path):
            return {"error": f"[v3-FINAL] Not Found at {data_path} (Check Time: {datetime.utcnow().isoformat()})"}
            
        rows = []
        with open(data_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['site_id'] == site_id and row['date'] == date:
                    # Map CSV fields to schema
                    row['type'] = f"Shift: {row['role']}"
                    row['timestamp'] = f"{row['date']}T{row['shift_start']}Z"
                    row['outcome'] = f"Active in {row['zone']}"
                    rows.append(row)
        
        return {
            "source": "Manual Shift Log",
            "format": "CSV",
            "data": normalize_list(rows, "Manual Entry System", "csv")
        }
    except Exception as e:
        return {"available": False, "error": str(e)}

