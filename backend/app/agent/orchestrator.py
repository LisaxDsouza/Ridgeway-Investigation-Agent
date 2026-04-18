import json
import groq
from sqlalchemy.orm import Session
from ..config import settings
from .prompts import SYSTEM_PROMPT, TOOL_SCHEMAS
from ..models import Incident, Event, DroneMission
from ..tools.signal_tools import retrieve_sensor_events, retrieve_access_logs, retrieve_vehicle_events
from ..tools.context_tools import get_weather_context, get_shift_schedule, get_site_metadata
from ..tools.drone_tools import simulate_drone_inspection

client = groq.Groq(api_key=settings.GROQ_API_KEY)

def dispatch_tool(name: str, args: dict, db: Session):
    """
    Dynamically call the appropriate tool function based on LLM request.
    """
    if name == "retrieveSensorEvents":
        return retrieve_sensor_events(db, **args)
    elif name == "retrieveAccessLogs":
        return retrieve_access_logs(db, **args)
    elif name == "getWeatherContext":
        return get_weather_context(**args)
    elif name == "getShiftSchedule":
        return get_shift_schedule(**args)
    elif name == "getSiteMetadata":
        return get_site_metadata(**args)
    elif name == "simulateDroneInspection":
        return simulate_drone_inspection(**args)
    return {"error": f"Tool {name} not found"}

def investigate_cluster(cluster_events: list, db: Session):
    """
    The main investigation loop for a single cluster of events.
    """
    # 1. Build initial context
    event_summaries = [f"{e.event_type} at {e.timestamp}" for e in cluster_events]
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Investigate this cluster of events: {json.dumps(event_summaries)}"}
    ]
    
    reasoning_trace = []
    
    # 2. Agent loop
    for _ in range(8): # Limit to 8 turns to prevent infinite loops
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto"
        )
        message = response.choices[0].message
        
        if message.tool_calls:
            messages.append(message)
            for tool_call in message.tool_calls:
                result = dispatch_tool(tool_call.function.name, 
                                       json.loads(tool_call.function.arguments), 
                                       db)
                
                reasoning_trace.append({
                    "tool": tool_call.function.name,
                    "query": tool_call.function.arguments,
                    "insight": str(result)[:200] + "..." # Truncate for trace
                })
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": json.dumps(result)
                })
        else:
            # Model finished investigation
            return persist_results(message.content, reasoning_trace, cluster_events, db)

    return None # Fallback if loop exceeded

def persist_results(raw_assessment: str, trace: list, events: list, db: Session):
    """
    Parse the LLM's final assessment and save it as an Incident.
    """
    # Simple parsing logic for MVP (assumes model follows instructions)
    # in production, we might force JSON output format
    lat_avg = sum(e.lat for e in events) / len(events)
    lon_avg = sum(e.lon for e in events) / len(events)
    
    incident = Incident(
        hypothesis=raw_assessment, # Store full assessment
        confidence_score=0.7, # Defaulting for now
        confidence_rationale="Investigation complete.",
        recommended_action="Review logs",
        reasoning_trace=trace,
        cluster_center_lat=lat_avg,
        cluster_center_lon=lon_avg
    )
    
    db.add(incident)
    db.flush() # Get ID
    
    # Link events to the incident
    for e in events:
        e.incident_id = incident.id
        db.add(e)
    
    db.commit()
    return incident
