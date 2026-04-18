from datetime import datetime, timedelta
from app.models import Event

def get_block_c_scenario():
    """
    Seeded data for the Block C scenario:
    - Fence alert @ 01:12
    - Vehicle activity @ 01:08-01:31
    - 3 Badge failures @ 01:15, 01:17, 01:22
    - Drone patrol @ 01:45-02:30
    - Weather: Wind 34 km/h
    """
    now = datetime.now()
    base_time = now.replace(hour=1, minute=0, second=0, microsecond=0)
    
    events = [
        # Vehicle activity near Gate 3
        {
            "event_type": "vehicle_detection",
            "source": "vehicle_tracking",
            "timestamp": base_time + timedelta(minutes=8),
            "lat": -25.8652, "lon": 28.1873,
            "metadata_json": {"vehicle_id": "V-9921", "speed": 12, "direction": "NE"}
        },
        # Fence vibration at Gate 3
        {
            "event_type": "fence_vibration",
            "source": "sensor",
            "timestamp": base_time + timedelta(minutes=12),
            "lat": -25.8655, "lon": 28.1875,
            "metadata_json": {"sensor_id": "F-G3-N", "intensity": 0.85}
        },
        # Failed badge swipes at Gate 3 North Pedestrian
        {
            "event_type": "failed_badge",
            "source": "gate_access",
            "timestamp": base_time + timedelta(minutes=15),
            "lat": -25.8651, "lon": 28.1872,
            "metadata_json": {"badge_id": "UNKNOWN", "gate_id": "G3-N-PED"}
        },
        {
            "event_type": "failed_badge",
            "source": "gate_access",
            "timestamp": base_time + timedelta(minutes=17),
            "lat": -25.8651, "lon": 28.1872,
            "metadata_json": {"badge_id": "UNKNOWN", "gate_id": "G3-N-PED"}
        },
        {
            "event_type": "failed_badge",
            "source": "gate_access",
            "timestamp": base_time + timedelta(minutes=22),
            "lat": -25.8651, "lon": 28.1872,
            "metadata_json": {"badge_id": "UNKNOWN", "gate_id": "G3-N-PED"}
        },
        # Routine noise (successful badge at Gate 1)
        {
            "event_type": "successful_badge",
            "source": "gate_access",
            "timestamp": base_time + timedelta(minutes=5),
            "lat": -25.8610, "lon": 28.1800,
            "metadata_json": {"badge_id": "B-4401", "gate_id": "G1-MAIN"}
        },
        # Routine noise (routine vehicle at Site Entrance)
        {
            "event_type": "vehicle_detection",
            "source": "vehicle_tracking",
            "timestamp": base_time + timedelta(minutes=30),
            "lat": -25.8600, "lon": 28.1790,
            "metadata_json": {"vehicle_id": "V-1022", "speed": 25, "direction": "S"}
        }
    ]
    
    # Add weather context (usually returned by tool, but seeded here for testing)
    # The agent will query this using its context tools
    
    return events
