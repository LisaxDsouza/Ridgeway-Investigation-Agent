import json
import groq
from sqlalchemy.orm import Session
from ..config import settings
from .prompts import SYSTEM_PROMPT, TOOL_SCHEMAS
from .evidence_graph import build_evidence_graph
from .confidence import calculate_incident_confidence
from ..models.incident import Incident
from ..mcp_server import server as mcp_root

client = groq.AsyncGroq(api_key=settings.GROQ_API_KEY)

async def dispatch_mcp_tool(name: str, args: dict):
    """
    Invoke the MCP tool handler logic.
    For MVP, we call the functions in the server directly.
    """
    try:
        # Since we use FastMCP, we can access the registered tools
        # The correct path in recent FastMCP versions is via the _tool_manager
        # This is a bit of a shortcut for the local dev loop
        tool_func = mcp_root.mcp._tool_manager._tools.get(name)
        if not tool_func:
            return {"error": f"Tool {name} not found"}
        
        # FastMCP tools are usually async
        result = await tool_func.fn(**args)
        print(f"[MCP] SUCCESS: {name}")
        return result
    except Exception as e:
        print(f"[MCP] ERROR: {name} - {str(e)}")
        return {"error": f"Execution failed: {str(e)}"}

async def investigate_cluster(cluster_events: list, db: Session, site_id: str):
    """
    The brain of the intelligence engine.
    Orchestrates multiple tool calls to form a forensic hypothesis.
    """
    # 1. Build initial context for Maya
    # Create relationship graph from raw signals
    graph = build_evidence_graph(cluster_events)
    
    event_summaries = [
        {
            "id": e.get('id'),
            "type": e.get('type') or e.get('source'),
            "zone": e.get('zone'),
            "time": e.get('recorded_at') or e.get('timestamp')
        } for e in cluster_events
    ]
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user", 
            "content": f"""SITE_ID: {site_id}
Target Signals: {json.dumps(event_summaries)}
Evidence Relationships: {json.dumps(graph)}

Begin forensic investigation. Use tools to gather context."""
        }
    ]
    
    reasoning_trace = []
    tool_calls_history = []
    
    # 2. Forensic Loop ( Maya )
    for turn in range(6): # Allow up to 6 forensic steps to stay within speed/token limits
        try:
            response = await client.chat.completions.create(
                model=settings.safe_groq_model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=0.1 # Keep investigation factual
            )
        except groq.RateLimitError:
            # Fallback to faster model with a small delay
            fallback_model = "llama-3.1-8b-instant"
            if settings.safe_groq_model == fallback_model: raise
            print(f" Maya: Rate limit hit. Waiting 5s then falling back to {fallback_model}.")
            await asyncio.sleep(5)
            response = await client.chat.completions.create(
                model=fallback_model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=0.1
            )
        except Exception as e:
            print(f"Maya Error on turn {turn+1}: {str(e)}")
            # Even on error, persist what we have so the signals are linked
            return await persist_incident(f"INTERRUPTED INVESTIGATION: {str(e)}", reasoning_trace, tool_calls_history, cluster_events, site_id, db, graph)
        
        message = response.choices[0].message
        messages.append(message)
        
        if not message.tool_calls:
            # Investigation complete!
            return await persist_incident(message.content, reasoning_trace, tool_calls_history, cluster_events, site_id, db, graph)
            
        # Handle Tool Calls
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Auto-inject site_id if missing in args
            if "site_id" not in args and name != "clusterEventsByLocation":
                args["site_id"] = site_id
            
            print(f" Maya Calling Tool: {name} with {args}")
            
            result = await dispatch_mcp_tool(name, args)
            
            from .tool_registry import TOOL_REGISTRY
            meta = TOOL_REGISTRY.get(name, {})
            
            # Log for the trace
            reasoning_trace.append({
                "step": turn + 1,
                "tool": name,
                "input": args,
                "outcome": str(result)[:500] + "...",
                "metadata": meta
            })
            
            tool_calls_history.append({
                "tool": name,
                "args": args,
                "result_keys": list(result.keys()) if isinstance(result, dict) else [],
                "metadata": meta
            })
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": name,
                "content": json.dumps(result)
            })

    return None

async def persist_incident(raw_summary: str, trace: list, calls: list, initial_events: list, site_id: str, db: Session, graph: dict = None):
    """
    Saves the final investigation as a formal Incident.
    """
    # Parse coordinates from initial events
    lats = [e.get('lat') for e in initial_events if e.get('lat')]
    lons = [e.get('lon') for e in initial_events if e.get('lon')]
    
    avg_lat = sum(lats)/len(lats) if lats else 12.9716 # fallback to site center
    avg_lon = sum(lons)/len(lons) if lons else 77.5946
    
    # 2. Dynamic Confidence Calculation
    # Factors in LLM reasoning + Tool Reliability metadata
    confidence, level, rationale = calculate_incident_confidence(raw_summary, calls)

    incident = Incident(
        site_id=site_id,
        hypothesis=raw_summary,
        confidence_score=confidence,
        confidence_level=level,
        confidence_rationale=rationale,
        recommended_action="Notify Supervisor" if confidence > 0.7 else "Monitor Zone",
        reasoning_trace={"steps": trace, "evidence_graph": graph},
        tool_calls_made=calls,
        related_event_ids=[e.get('id') for e in initial_events],
        cluster_centroid_lat=avg_lat,
        cluster_centroid_lon=avg_lon,
        triggered_by="scheduled"
    )
    
    db.add(incident)
    db.commit()
    db.refresh(incident)
    
    # 3. LINKAGE: Mark raw signals as investigated so they aren't clustered again
    from ..models import SensorReading, AccessEvent, VehicleDetection, DroneTelemetry
    for event in initial_events:
        e_type = event.get('type')
        e_id = event.get('id')
        if not e_id: continue
        
        try:
            if e_type == 'sensor':
                db.query(SensorReading).filter(SensorReading.id == e_id).update({"incident_id": incident.id})
            elif e_type == 'access':
                db.query(AccessEvent).filter(AccessEvent.id == e_id).update({"incident_id": incident.id})
            elif e_type == 'vehicle':
                db.query(VehicleDetection).filter(VehicleDetection.id == e_id).update({"incident_id": incident.id})
        except Exception as e:
            print(f"Failed to link signal {e_id}: {e}")
            
    db.commit()
    print(f"[SEARCH] Incident persisted: {incident.id} (Confidence: {level})")
    return incident
