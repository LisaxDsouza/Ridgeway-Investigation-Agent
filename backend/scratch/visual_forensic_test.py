import asyncio
import sys
import os
import json
from datetime import datetime, timedelta

# Add parent directory to path to allow imports from 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent import orchestrator
from app.database import SessionLocal
from app.config import settings

# 1. VISUAL WRAPPER FOR MCP
# We override the default dispatcher to show the "MCP Protocol" hop visually
original_dispatch = orchestrator.dispatch_mcp_tool

async def visual_mcp_dispatcher(name: str, args: dict):
    print(f"\n    [-- MCP PROTOCOL LAYER] Routing Tool: \033[1;36m{name}\033[0m")
    print(f"    [ARGS] {json.dumps(args)}")
    
    # Call the original logic
    result = await original_dispatch(name, args)
    
    if isinstance(result, dict) and 'error' in result:
        print(f"    [!] ERROR: {result['error']}")
    
    print(f"    [DATA FETCHED] Keys: {list(result.keys()) if isinstance(result, dict) else 'Scalar result'}")
    return result

# Patch the orchestrator
orchestrator.dispatch_mcp_tool = visual_mcp_dispatcher

async def simulate_mystery_incident():
    print(f"\n" + ">>"*10 + " STARTING VISUAL FORENSIC INVESTIGATION " + "<<"*10)
    print(f"[*] Target Site: {settings.SITE_ID}")
    print(f"[*] Agent Model: {settings.GROQ_MODEL}")
    print("-" * 80)

    # 1. CREATE A MYSTERY SCENARIO
    # We mock a cluster of signals that should trigger investigation:
    # 1. A fence vibration in a restricted zone.
    # 2. An unrecognized badge swipe nearby at the exact same time.
    
    now = datetime.utcnow()
    two_hours_ago = now - timedelta(hours=2)
    timestamp = two_hours_ago.isoformat() + "Z"
    
    mock_events = [
        {
            "id": "mock-sig-001",
            "type": "fence_vibration",
            "zone": "block-c-perimeter",
            "lat": 12.9716,
            "lon": 77.5946,
            "recorded_at": timestamp,
            "source": "sensor-f-09"
        },
        {
            "id": "mock-sig-002",
            "type": "unauthorized_badge",
            "zone": "block-c-gate",
            "lat": 12.9715,
            "lon": 77.5945,
            "recorded_at": timestamp,
            "source": "access-reader-g2"
        }
    ]

    print(f"[*] INGESTED OVERNIGHT SIGNALS: {len(mock_events)}")
    for e in mock_events:
        print(f"    - {e['recorded_at']} | {e['type']} @ {e['zone']}")

    print("\n" + ">>> MAYA (AI AGENT) TAKING OVER <<<")
    
    # 2. RUN INVESTIGATION
    # We use a database session for the duration
    with SessionLocal() as db:
        try:
            incident = await orchestrator.investigate_cluster(
                cluster_events=mock_events,
                db=db,
                site_id=settings.SITE_ID
            )
            
            print("\n" + "="*80)
            print("INVESTIGATION COMPLETE")
            print("="*80)
            print(f"\n[FINAL HYPOTHESIS]\n{incident.hypothesis}")
            print(f"\n[CONFIDENCE] {incident.confidence_score*100}% ({incident.confidence_level})")
            print(f"[RECOMMENDATION] {incident.recommended_action}")
            
            print(f"\n[REASONING TRACE]")
            for step in incident.reasoning_trace.get('steps', []):
                print(f"   Turn {step['step']}: Used {step['tool']} to check {list(step['input'].keys())}")
                
        except Exception as e:
            print(f"\n[ERROR] Investigation failed: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simulate_mystery_incident())
