# Normalization layer for heterogeneous data sources
# Ensures the LLM sees a unified structure regardless of whether data came from PostgreSQL, CSV, JSON, or SQLite.

def normalize_evidence(raw_data, source_name, storage_format):
    """
    Standardizes a raw record into the forensic evidence schema.
    """
    # Common fields we want for every piece of evidence
    normalized = {
        "metadata": {
            "source": source_name,
            "format": storage_format,
            "ingested_at": None # Could add current time
        },
        "event": {
            "timestamp": raw_data.get("recorded_at") or raw_data.get("timestamp") or raw_data.get("date"),
            "type": raw_data.get("sensor_type") or raw_data.get("event_type") or raw_data.get("type"),
            "zone": raw_data.get("zone") or "unknown",
            "lat": raw_data.get("lat"),
            "lon": raw_data.get("lon"),
            "value": raw_data.get("raw_value") or raw_data.get("outcome") or raw_data.get("value")
        }
    }
    
    # Handle specific fields for different types
    if "vehicle_id" in raw_data:
        normalized["event"]["subject"] = f"Vehicle: {raw_data['vehicle_id']}"
    elif "badge_id" in raw_data:
        normalized["event"]["subject"] = f"Badge: {raw_data['badge_id']}"
    elif "user" in raw_data:
        normalized["event"]["subject"] = f"User: {raw_data['user']}"

    return normalized

def normalize_list(data_list, source_name, storage_format):
    return [normalize_evidence(item, source_name, storage_format) for item in data_list]
