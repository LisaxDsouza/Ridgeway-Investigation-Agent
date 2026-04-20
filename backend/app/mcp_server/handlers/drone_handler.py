import json
import os
from ...agent.evidence_schema import normalize_list
from ..utils import get_data_source_path

async def handle(site_id, start_time, end_time, mission_id, flagged_only):
    try:
        data_path = get_data_source_path('drone_logs.json')
        if not os.path.exists(data_path):
            return {"error": "Drone log source not found."}
            
        with open(data_path, 'r') as f:
            raw_data = json.load(f)
            
        # Filter by mission_id or site (simple filter for simulation)
        # Note: site_id isn't in my mock JSON yet, I'll assume site_id filter elsewhere or just use mission_id
        filtered_data = raw_data
        if mission_id:
            filtered_data = [d for d in raw_data if d['mission_id'] == mission_id]
        
        return {
            "source": "Autonomous Drone Cluster (JSON)",
            "format": "JSON",
            "data": normalize_list(filtered_data, "Autonomous Drone Logs", "json")
        }
    except Exception as e:
        return {"available": False, "error": str(e)}

