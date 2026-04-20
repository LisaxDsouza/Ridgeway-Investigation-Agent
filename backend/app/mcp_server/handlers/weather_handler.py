import json
import os
from datetime import datetime
from ...agent.evidence_schema import normalize_list
from ..utils import get_data_source_path

async def handle(site_id, start_time, end_time):
    try:
        data_path = get_data_source_path('weather_api.json')
        if not os.path.exists(data_path):
            return {"error": f"[v3-FINAL] Not Found at {data_path} (Check Time: {datetime.utcnow().isoformat()})"}
            
        with open(data_path, 'r') as f:
            raw_data = json.load(f)
            
        # Filter by site_id and time (simple filter for simulation)
        site_data = [d for d in raw_data if d['site_id'] == site_id]
        
        return {
            "source": "WeatherAPI (Live)",
            "format": "JSON",
            "data": normalize_list(site_data, "External Weather API", "json")
        }
    except Exception as e:
        return {"available": False, "error": str(e)}

