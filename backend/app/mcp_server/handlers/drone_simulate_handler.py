from ...tools.drone_tools import simulate_drone_inspection

async def handle(target_lat, target_lon, incident_id):
    try:
        # Pass parameters to simulation tool
        result = simulate_drone_inspection(target_lat, target_lon)
        
        # Link to incident ID in result if provided
        if incident_id:
            result['incident_id'] = incident_id
            
        return result
    except Exception as e:
        return {"status": "failed", "error": str(e)}
