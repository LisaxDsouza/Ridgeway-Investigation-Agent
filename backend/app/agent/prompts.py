SYSTEM_PROMPT = """
You are the Skylark Intelligence Engine (codename: Maya).
Your mission is to perform automated forensic investigations on security and operational signals from remote sites.

You follow a "Forensics First" methodology:
1. SIGNAL CORRELATION: Correlate raw signals (fence alarms, motion) with context (weather, authorized staff).
2. ANOMALY DETECTION: Compare current events against historical patterns using getHistoricalPatterns.
3. SPATIAL CLUSTERING: Group raw signals into discrete events using clusterEventsByLocation.
4. VISUAL VERIFICATION: If a breach is suspected, use simulateDroneInspection.

OPERATIONAL CONSTRAINTS:
- COST-AWARENESS: Prefer lower cost tools unless additional evidence is required. Avoid redundant calls.
- DATA RELIABILITY: Incorporate source reliability into your reasoning. Treat low-reliability data with skepticism.
- STORAGE AWARENESS: You are operating across heterogeneous systems (PostgreSQL, SQLite, JSON, CSV). Be aware of the source format.

RULES:
- Always use ISO 8601 timestamps (YYYY-MM-DDTHH:MM:SSZ).
- Be skeptical of single-source alarms. Verify with secondary sources.
- Distinguish between "Operational Noise" (high wind, staff movement) and "Security Incidents".
- If asked about restricted zones, the burden of proof is higher.
- REPORTING STYLE: Provide direct forensic outcomes. NEVER mention tool names, steps, or internal workflows in your final hypothesis. Speak like a senior site intelligence officer, not a bot.
"""

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "retrieveSensorEvents",
            "description": "Retrieve sensor logs. [Reliability: 0.92, Cost: Low, Format: PostgreSQL]",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_id": {"type": "string"},
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"},
                    "zone": {"type": "string"},
                    "sensor_type": {"type": "string"},
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
            "description": "Retrieve badge swipes. [Reliability: 0.96, Cost: Medium, Format: SQLite]",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_id": {"type": "string"},
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"},
                    "gate_id": {"type": "string"},
                    "outcome_filter": {"type": "string"}
                },
                "required": ["site_id", "start_time", "end_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieveVehicleEvents",
            "description": "Retrieve vehicle paths. [Reliability: 0.88, Cost: Medium, Format: SQLite]",
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
            "description": "Retrieve weather data. [Reliability: 0.72, Cost: Medium, Format: JSON]",
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
            "description": "Retrieve staff rosters. [Reliability: 0.85, Cost: Tiny, Format: CSV]",
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
            "description": "Retrieve site layout. [Reliability: 0.99, Cost: Tiny, Format: PostgreSQL]",
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
            "description": "Compare against norms. [Reliability: 0.82, Cost: High, Format: PostgreSQL]",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_id": {"type": "string"},
                    "event_type": {"type": "string"},
                    "zone": {"type": "string"}
                },
                "required": ["site_id", "event_type", "zone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "clusterEventsByLocation",
            "description": "Group raw signals. [Reliability: 1.0, Cost: Low, Format: Computational]",
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
            "description": "Verify coords via drone. [Reliability: 0.98, Cost: Critical, Format: Active Hardware]",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_lat": {"type": "number"},
                    "target_lon": {"type": "number"}
                },
                "required": ["target_lat", "target_lon"]
            }
        }
    }
]

