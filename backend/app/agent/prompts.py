SYSTEM_PROMPT = """
You are the Ridgeway Site Overnight Intelligence Assistant. Your role is investigator, not summarizer.
You receive a cluster of overnight signals (fence alarms, badge swipes, vehicle detections, etc.).
Your goal is to form a hypothesis about what happened and recommend an action.

RULES:
1. Don't guess. Use your context tools to verify hypotheses (e.g., check weather for wind, check shift schedule for authorized personnel).
2. Report uncertainty honestly. Use confidence_score (0.0 to 1.0) and confidence_rationale.
3. If evidence is thin, call more tools before concluding.
4. Output must be a structured assessment of the incident.
5. IMPORTANT: All date-time parameters for tools MUST be in strict ISO 8601 format (e.g., "2026-04-18T02:00:00Z").
"""

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "retrieveSensorEvents",
            "description": "Retrieve raw sensor telemetry (e.g., fence vibrations) for a time window.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {"type": "string", "description": "Start time in ISO 8601 format (e.g. 2026-04-18T00:00:00Z)"},
                    "end_time": {"type": "string", "description": "End time in ISO 8601 format (e.g. 2026-04-18T02:00:00Z)"},
                    "zone": {"type": "string", "description": "Optional site zone filter"}
                },
                "required": ["start_time", "end_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieveAccessLogs",
            "description": "Retrieve gate access and badge swipe events.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {"type": "string", "description": "Start time in ISO 8601 format (e.g. 2026-04-18T00:00:00Z)"},
                    "end_time": {"type": "string", "description": "End time in ISO 8601 format (e.g. 2026-04-18T02:00:00Z)"},
                    "gate": {"type": "string", "description": "Optional gate ID filter"}
                },
                "required": ["start_time", "end_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getWeatherContext",
            "description": "Get weather conditions (wind, visibility) for a specific date and site.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date in ISO 8601 format (e.g. 2026-04-18T02:00:00Z)"},
                    "site_id": {"type": "string", "default": "ridgeway"}
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getShiftSchedule",
            "description": "Retrieve the roster of personnel on duty for a specific date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date in ISO 8601 format (e.g. 2026-04-18T02:00:00Z)"}
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "getSiteMetadata",
            "description": "Get definitions and rules for specific site zones.",
            "parameters": {
                "type": "object",
                "properties": {
                    "zone": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "simulateDroneInspection",
            "description": "Trigger a simulated drone patrol over an incident location to gather visual/thermal signatures.",
            "parameters": {
                "type": "object",
                "properties": {
                    "incident_id": {"type": "string"},
                    "target_location": {
                        "type": "object",
                        "properties": {
                            "lat": {"type": "number"},
                            "lon": {"type": "number"}
                        },
                        "required": ["lat", "lon"]
                    }
                },
                "required": ["incident_id", "target_location"]
            }
        }
    }
]
