from datetime import datetime
from typing import Optional

def get_weather_context(date: datetime, site_id: str = "ridgeway"):
    """
    Wind speed (km/h), direction, precipitation, visibility (overnight window)
    """
    # MVP: Returning seeded mock data for the overnight window
    # In production, this would query a weather API or a historical table
    return {
        "wind_speed": 34.0,
        "wind_direction": "NE",
        "precipitation": "none",
        "visibility": "clear",
        "note": "Wind speed is above fence vibration thresholds (25 km/h)."
    }

def get_shift_schedule(date: datetime):
    """
    Shift roster: who on duty, expected activity zones, scheduled maintenance
    """
    return {
        "shift_lead": "Maya",
        "on_duty": ["John", "Sarah", "Mike"],
        "activity_zones": ["Gate 1", "Block C", "Admin"],
        "maintenance": "None scheduled"
    }

def get_site_metadata(zone: Optional[str] = None):
    """
    Zone definitions, access rules, restricted areas, expected vehicle presence
    """
    site_map = {
        "Block C": {
            "type": "Restricted Yard",
            "access_level": "Level 3",
            "notes": "No civilian vehicles expected after 22:00."
        },
        "Gate 3": {
            "type": "Perimeter Access",
            "access_level": "Level 2",
            "notes": "Frequent false alarms during high wind."
        }
    }
    if zone:
        return site_map.get(zone, {"error": "Zone not found"})
    return site_map

def get_historical_patterns(event_type: str, zone: str, lookback_days: int = 30):
    """
    Frequency + characteristics of similar past events (mock data in MVP)
    """
    return {
        "similar_events_count": 12,
        "common_cause": "wind_vibration",
        "confidence_in_pattern": 0.85
    }
