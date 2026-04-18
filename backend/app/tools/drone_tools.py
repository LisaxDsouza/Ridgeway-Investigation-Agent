from typing import Dict, List
import random

def simulate_drone_inspection(incident_id: str, target_location: Dict[str, float]):
    """
    Simulated GeoJSON path + findings object with waypoint observations.
    """
    lat, lon = target_location['lat'], target_location['lon']
    
    # Generate a simple square/circular flight path around the target
    path = [
        [lon, lat],
        [lon + 0.001, lat],
        [lon + 0.001, lat + 0.001],
        [lon, lat + 0.001],
        [lon, lat]
    ]
    
    waypoints = [
        {"timestamp": "01:46", "observation": "Approaching target location.", "flag": False},
        {"timestamp": "01:48", "observation": "Visual on restricted yard fence. No obvious breach.", "flag": False},
        {"timestamp": "01:50", "observation": "Detecting residual heat signature near Gate 3.", "flag": True},
        {"timestamp": "01:52", "observation": "Mission complete. Returning to base.", "flag": False}
    ]
    
    return {
        "mission_id": f"MD-{random.randint(1000, 9999)}",
        "incident_id": incident_id,
        "path_geojson": {
            "type": "LineString",
            "coordinates": path
        },
        "waypoints": waypoints,
        "summary": "Drone identified a thermal signature but no physical intruder detected."
    }
