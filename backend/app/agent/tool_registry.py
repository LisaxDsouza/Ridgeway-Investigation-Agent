# Central Registry for Investigative Tools
# Metadata used for agent reasoning, confidence scoring, and cost-aware planning.

TOOL_REGISTRY = {
    "retrieveSensorEvents": {
        "reliability": 0.92,
        "cost": 0.2,
        "latency": 150,
        "source_type": "internal_sensor",
        "storage_format": "postgresql"
    },
    "retrieveAccessLogs": {
        "reliability": 0.96,
        "cost": 0.4,
        "latency": 300,
        "source_type": "access_control",
        "storage_format": "sqlite"
    },
    "retrieveVehicleEvents": {
        "reliability": 0.88,
        "cost": 0.5,
        "latency": 450,
        "source_type": "vendor_tracking",
        "storage_format": "sqlite"
    },
    "getWeatherContext": {
        "reliability": 0.72,
        "cost": 0.3,
        "latency": 600,
        "source_type": "external_api",
        "storage_format": "json"
    },
    "getShiftSchedule": {
        "reliability": 0.85,
        "cost": 0.1,
        "latency": 100,
        "source_type": "manual_entry",
        "storage_format": "csv"
    },
    "retrieveDroneLogs": {
        "reliability": 0.94,
        "cost": 0.7,
        "latency": 400,
        "source_type": "autonomous_drone",
        "storage_format": "json"
    },
    "getSiteMetadata": {
        "reliability": 0.99,
        "cost": 0.1,
        "latency": 50,
        "source_type": "facility_master_data",
        "storage_format": "postgresql"
    },
    "getHistoricalPatterns": {
        "reliability": 0.82,
        "cost": 0.6,
        "latency": 1200,
        "source_type": "analytics_lab",
        "storage_format": "postgresql"
    },
    "simulateDroneInspection": {
        "reliability": 0.98,
        "cost": 0.9,
        "latency": 5000,
        "source_type": "real_time_drone",
        "storage_format": "active_system"
    }
}
