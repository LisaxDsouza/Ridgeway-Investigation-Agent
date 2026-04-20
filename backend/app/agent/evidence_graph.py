from datetime import datetime
import math

def spatial_distance(lat1, lon1, lat2, lon2):
    """Calculates rough distance in meters between two coordinates."""
    if None in [lat1, lon1, lat2, lon2]:
        return 99999
    
    # Approx: 1 deg = 111km
    dlat = (lat1 - lat2) * 111000
    dlon = (lon1 - lon2) * 111000 * math.cos(math.radians(lat1))
    return math.sqrt(dlat**2 + dlon**2)

def build_evidence_graph(events):
    """
    Builds a lightweight evidence graph showing spatial and temporal relationships.
    Helps the agent see clusters and causal links.
    """
    nodes = []
    edges = []

    # 1. Create Nodes
    for i, event in enumerate(events):
        nodes.append({
            "id": i,
            "type": event.get("type") or event.get("source"),
            "time": event.get("recorded_at") or event.get("timestamp")
        })

    # 2. Identify Relationships (Edges)
    for i, e1 in enumerate(events):
        for j, e2 in enumerate(events):
            if i >= j: continue
            
            reasons = []
            
            # Spatial proximity (< 50m)
            dist = spatial_distance(e1.get('lat'), e1.get('lon'), e2.get('lat'), e2.get('lon'))
            if dist < 50:
                reasons.append(f"nearby ({dist:.1f}m)")
            
            # Temporal proximity (< 5 minutes)
            try:
                t1 = datetime.fromisoformat((e1.get('recorded_at') or e1.get('timestamp')).replace('Z', '+00:00'))
                t2 = datetime.fromisoformat((e2.get('recorded_at') or e2.get('timestamp')).replace('Z', '+00:00'))
                time_diff = abs((t1 - t2).total_seconds())
                if time_diff < 300:
                    reasons.append(f"co-incident ({time_diff:.0f}s)")
            except:
                pass
                
            if reasons:
                edges.append({
                    "source": i,
                    "target": j,
                    "relation": " & ".join(reasons)
                })

    return {
        "nodes": nodes,
        "edges": edges,
        "summary": f"Detected {len(edges)} significant relationships across {len(nodes)} signals."
    }
