SYSTEM_PROMPT = """
You are the Skylark Intelligence Engine (codename: Maya).
Your mission is to perform automated forensic investigations on security and operational signals from remote sites.

You follow a "Forensics First" methodology:
1. SIGNAL CORRELATION: Correlate raw signals (fence alarms, motion) with context (weather, authorized staff).
2. ANOMALY DETECTION: Compare current events against historical patterns using getHistoricalPatterns.
3. SPATIAL CLUSTERING: Group raw signals into discrete events using clusterEventsByLocation.
4. VISUAL VERIFICATION: If a breach is suspected, use simulateDroneInspection.

RULES:
- Always use ISO 8601 timestamps (YYYY-MM-DDTHH:MM:SSZ).
- Be skeptical of single-source alarms. Verify with secondary sources (e.g., fence alarm + badge swipe + weather).
- Distinguish between "Operational Noise" (high wind, staff movement) and "Security Incidents".
- If evidence is clear but low-confidence, explain why in confidence_rationale.
- For restricted zones, the burden of proof is higher.
"""

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "retrieveSensorEvents",
            "description": "Retrieve detailed sensor logs (vibration, perimeter, motion) for a time window.",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_id": {"type": "string"},
                    "start_time": {"type": "string", "description": "ISO format timestamp"},
                    "end_time": {"type": "string", "description": "ISO format timestamp"},
                    "zone": {"type": "string", "description": "Optional zone filter (block-a, etc)"},
                    "sensor_type": {"type": "string", "description": "fence_vibration | motion | perimeter"},
                    "breached_only": {"type": "boolean", "default": False}
                },
                "required": ["site_id", "start_time", "end_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieveAccessLogs",
            "description": "Retrieve badge swipe and gate operation logs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_id": {"type": "string"},
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"},
                    "gate_id": {"type": "string"},
                    "outcome_filter": {"type": "string", "description": "success | fail"}
                },
                "required": ["site_id", "start_time", "end_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieveVehicleEvents",
            "description": "Retrieve vehicle detections and reconstructed movement paths.",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_id": {"type": "string"},
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"},
                    "zone": {"type": "string"},
                    "restricted_only": {"type": "boolean", "default": False}
                },
                "required": ["site_id", "start_time", "end_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getWeatherContext",
            "description": "Retrieve high-resolution weather data (wind, visibility).",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_id": {"type": "string"},
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"}
                },
                "required": ["site_id", "start_time", "end_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getShiftSchedule",
            "description": "Retrieve staff rosters and active site zones.",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_id": {"type": "string"},
                    "date": {"type": "string", "description": "YYYY-MM-DD"}
                },
                "required": ["site_id", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getSiteMetadata",
            "description": "Retrieve site layout, zone boundaries, and classification.",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_id": {"type": "string"},
                    "zone_id": {"type": "string"}
                },
                "required": ["site_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getHistoricalPatterns",
            "description": "Compare current events against historical norms to detect anomalies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_id": {"type": "string"},
                    "event_type": {"type": "string"},
                    "zone": {"type": "string"},
                    "lookback_days": {"type": "integer", "default": 30}
                },
                "required": ["site_id", "event_type", "zone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "clusterEventsByLocation",
            "description": "Group raw signals into discrete spatial clusters using DBSCAN.",
            "parameters": {
                "type": "object",
                "properties": {
                    "events": {
                        "type": "array",
                        "items": {"type": "object"}
                    }
                },
                "required": ["events"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "simulateDroneInspection",
            "description": "Dispatch a simulated drone to verify specific coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_lat": {"type": "number"},
                    "target_lon": {"type": "number"},
                    "incident_id": {"type": "string"}
                },
                "required": ["target_lat", "target_lon"]
            }
        }
    }
]
