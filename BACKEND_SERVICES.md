# Backend Services — Implementation Specification
## ridgeway-intelligence / backend

This document tells you exactly what to build, file by file, for every backend
layer that does not yet exist or needs to be expanded. Read it alongside the
architecture document. The directory tree at the top of each section shows
where the file lives.

---

## 0. Ground Rules

**The agent never touches the database directly.**
The call chain is always:

```
Groq agent
  → MCP tool call
    → MCP handler (validates, dispatches)
      → data_service (queries DB, shapes result)
        → SQLAlchemy session
          → isolated table
```

No shortcutting. If a tool handler queries the DB directly it is wrong.
If the orchestrator queries the DB for anything other than the initial
event fetch and persistence, it is wrong.

---

## 1. Database Layer — Isolated Source Tables

### What exists now
`models/event.py` — a single generic event model.

### What needs to change
Replace the single `event.py` with six source-specific tables.
Keep the existing `incident.py`, `briefing.py`, `drone_mission.py` but
expand them as described below.

---

### 1.1 `models/sensor_readings.py` — NEW

Stores every fence, perimeter, motion, and environmental sensor event.

```python
class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id                  = Column(UUID, primary_key=True, default=uuid4)
    recorded_at         = Column(DateTime(timezone=True), nullable=False)
    site_id             = Column(String(64), nullable=False)
    zone                = Column(String(64), nullable=False)
    sensor_id           = Column(String(128), nullable=False)
    sensor_type         = Column(String(64), nullable=False)
    # sensor_type values: fence_vibration | motion | perimeter | env_temp | env_wind
    raw_value           = Column(Numeric)
    unit                = Column(String(32))
    threshold           = Column(Numeric)
    threshold_breached  = Column(Boolean, nullable=False, default=False)
    lat                 = Column(Numeric(10, 7))
    lon                 = Column(Numeric(10, 7))
    metadata_json       = Column(JSONB, default={})
```

**Indexes required:**
```sql
CREATE INDEX idx_sensor_site_time   ON sensor_readings (site_id, recorded_at DESC);
CREATE INDEX idx_sensor_zone_type   ON sensor_readings (zone, sensor_type, recorded_at DESC);
CREATE INDEX idx_sensor_breached    ON sensor_readings (threshold_breached, recorded_at DESC)
    WHERE threshold_breached = TRUE;
```

---

### 1.2 `models/access_events.py` — NEW

Stores badge swipes, gate operations, access control events.

```python
class AccessEvent(Base):
    __tablename__ = "access_events"

    id              = Column(UUID, primary_key=True, default=uuid4)
    recorded_at     = Column(DateTime(timezone=True), nullable=False)
    site_id         = Column(String(64), nullable=False)
    gate_id         = Column(String(128), nullable=False)
    zone            = Column(String(64), nullable=False)
    badge_id        = Column(String(128))
    person_id       = Column(String(128))
    outcome         = Column(String(32), nullable=False)
    # outcome values: success | fail | forced | tailgate
    failure_reason  = Column(String(128))
    # failure_reason values: wrong_zone | expired | unknown_badge | after_hours
    lat             = Column(Numeric(10, 7))
    lon             = Column(Numeric(10, 7))
    metadata_json   = Column(JSONB, default={})
```

**Indexes required:**
```sql
CREATE INDEX idx_access_site_time   ON access_events (site_id, recorded_at DESC);
CREATE INDEX idx_access_gate_time   ON access_events (gate_id, recorded_at DESC);
CREATE INDEX idx_access_outcome     ON access_events (outcome, recorded_at DESC)
    WHERE outcome != 'success';
CREATE INDEX idx_access_badge       ON access_events (badge_id, recorded_at DESC);
```

---

### 1.3 `models/vehicle_detections.py` — NEW

Stores vehicle tracking events and path segments.

```python
class VehicleDetection(Base):
    __tablename__ = "vehicle_detections"

    id               = Column(UUID, primary_key=True, default=uuid4)
    recorded_at      = Column(DateTime(timezone=True), nullable=False)
    site_id          = Column(String(64), nullable=False)
    zone             = Column(String(64), nullable=False)
    vehicle_id       = Column(String(128))
    vehicle_type     = Column(String(64))
    # vehicle_type values: forklift | truck | car | unknown
    lat              = Column(Numeric(10, 7), nullable=False)
    lon              = Column(Numeric(10, 7), nullable=False)
    speed_kmh        = Column(Numeric(6, 2))
    heading_deg      = Column(Numeric(6, 2))
    in_restricted    = Column(Boolean, nullable=False, default=False)
    path_segment_id  = Column(String(128))
    # path_segment_id groups sequential detections into one vehicle path
    metadata_json    = Column(JSONB, default={})
```

**Indexes required:**
```sql
CREATE INDEX idx_vehicle_site_time    ON vehicle_detections (site_id, recorded_at DESC);
CREATE INDEX idx_vehicle_zone         ON vehicle_detections (zone, recorded_at DESC);
CREATE INDEX idx_vehicle_restricted   ON vehicle_detections (in_restricted, recorded_at DESC)
    WHERE in_restricted = TRUE;
CREATE INDEX idx_vehicle_path         ON vehicle_detections (path_segment_id, recorded_at ASC);
```

---

### 1.4 `models/drone_telemetry.py` — NEW

Stores drone patrol paths and per-waypoint observations.
This is different from `drone_mission.py` — telemetry is the raw positional
log. `drone_mission.py` is the agent's output (simulated follow-up mission).

```python
class DroneTelemetry(Base):
    __tablename__ = "drone_telemetry"

    id              = Column(UUID, primary_key=True, default=uuid4)
    recorded_at     = Column(DateTime(timezone=True), nullable=False)
    site_id         = Column(String(64), nullable=False)
    mission_id      = Column(String(128), nullable=False)
    mission_type    = Column(String(64), nullable=False)
    # mission_type values: scheduled | follow_up | manual
    drone_id        = Column(String(128), nullable=False)
    lat             = Column(Numeric(10, 7), nullable=False)
    lon             = Column(Numeric(10, 7), nullable=False)
    altitude_m      = Column(Numeric(8, 2))
    heading_deg     = Column(Numeric(6, 2))
    waypoint_index  = Column(Integer)
    observation     = Column(Text)
    flagged         = Column(Boolean, nullable=False, default=False)
    flag_reason     = Column(Text)
    metadata_json   = Column(JSONB, default={})
```

**Indexes required:**
```sql
CREATE INDEX idx_drone_mission_time   ON drone_telemetry (mission_id, recorded_at ASC);
CREATE INDEX idx_drone_site_time      ON drone_telemetry (site_id, recorded_at DESC);
CREATE INDEX idx_drone_flagged        ON drone_telemetry (flagged, recorded_at DESC)
    WHERE flagged = TRUE;
```

---

### 1.5 `models/weather_readings.py` — NEW

```python
class WeatherReading(Base):
    __tablename__ = "weather_readings"

    id               = Column(UUID, primary_key=True, default=uuid4)
    recorded_at      = Column(DateTime(timezone=True), nullable=False)
    site_id          = Column(String(64), nullable=False)
    wind_kmh         = Column(Numeric(6, 2))
    wind_direction   = Column(String(16))
    gust_kmh         = Column(Numeric(6, 2))
    temp_c           = Column(Numeric(5, 2))
    humidity_pct     = Column(Numeric(5, 2))
    visibility_m     = Column(Numeric(8, 2))
    precipitation    = Column(String(32))
    # precipitation values: none | light_rain | heavy_rain | fog
    pressure_hpa     = Column(Numeric(8, 2))
```

**Critical:** Seed weather at 15-minute intervals, not as a single overnight
record. The agent needs `readings_by_15min` to avoid drawing wrong conclusions
from coarse aggregates.

**Indexes required:**
```sql
CREATE INDEX idx_weather_site_time    ON weather_readings (site_id, recorded_at DESC);
```

---

### 1.6 `models/site_metadata.py` — NEW

Two tables: zones and shift schedules. Static reference data.

```python
class SiteZone(Base):
    __tablename__ = "site_zones"

    id                  = Column(UUID, primary_key=True, default=uuid4)
    site_id             = Column(String(64), nullable=False)
    zone_id             = Column(String(128), nullable=False, unique=True)
    zone_name           = Column(String(256))
    zone_type           = Column(String(64))
    # zone_type values: perimeter | storage | workzone | access | restricted
    is_restricted       = Column(Boolean, nullable=False, default=False)
    access_rules        = Column(JSONB, default={})
    # access_rules shape: { allowed_roles, allowed_hours, requires_escort }
    boundary_geojson    = Column(JSONB)
    expected_vehicles   = Column(Boolean, default=False)
    notes               = Column(Text)


class ShiftSchedule(Base):
    __tablename__ = "shift_schedule"

    id                      = Column(UUID, primary_key=True, default=uuid4)
    site_id                 = Column(String(64), nullable=False)
    shift_date              = Column(Date, nullable=False)
    shift_type              = Column(String(32), nullable=False)
    # shift_type values: day | night | weekend
    shift_start             = Column(DateTime(timezone=True), nullable=False)
    shift_end               = Column(DateTime(timezone=True), nullable=False)
    supervisor_id           = Column(String(128))
    headcount               = Column(Integer)
    active_zones            = Column(JSONB, default=[])
    scheduled_maintenance   = Column(JSONB, default=[])
```

---

### 1.7 `models/investigation_runs.py` — NEW

Tracks every investigation job, scheduled or hook-triggered.

```python
class InvestigationRun(Base):
    __tablename__ = "investigation_runs"

    id                  = Column(UUID, primary_key=True, default=uuid4)
    created_at          = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at        = Column(DateTime(timezone=True))
    site_id             = Column(String(64), nullable=False)
    trigger_type        = Column(String(64), nullable=False)
    # trigger_type values: scheduled | incident_hook | manual
    trigger_source      = Column(String(128))
    # trigger_source: hook_id if incident_hook, "cron" if scheduled
    status              = Column(String(32), nullable=False, default="queued")
    # status values: queued | running | complete | failed
    window_start        = Column(DateTime(timezone=True), nullable=False)
    window_end          = Column(DateTime(timezone=True), nullable=False)
    events_fetched      = Column(Integer, default=0)
    clusters_found      = Column(Integer, default=0)
    incidents_created   = Column(Integer, default=0)
    error_message       = Column(Text)
```

---

### 1.8 `models/hook_events.py` — NEW

Audit table for all incident hook submissions.

```python
class HookEvent(Base):
    __tablename__ = "hook_events"

    id                  = Column(UUID, primary_key=True, default=uuid4)
    created_at          = Column(DateTime(timezone=True), default=datetime.utcnow)
    site_id             = Column(String(64), nullable=False)
    submitted_by        = Column(String(128), nullable=False)
    observation         = Column(Text, nullable=False)
    zone                = Column(String(64))
    lat                 = Column(Numeric(10, 7))
    lon                 = Column(Numeric(10, 7))
    severity_hint       = Column(String(16))
    # severity_hint values: low | medium | high
    lookback_minutes    = Column(Integer, nullable=False, default=120)
    include_sources     = Column(JSONB, default=["sensor","vehicle","access","drone","weather"])
    notes               = Column(Text)
    status              = Column(String(32), nullable=False, default="queued")
    # status values: queued | processing | complete | failed
    run_id              = Column(UUID, ForeignKey("investigation_runs.id"))
    incident_id         = Column(UUID, ForeignKey("incidents.id"))
    error_message       = Column(Text)
```

---

### 1.9 Expand `models/incident.py` — MODIFY

Add these fields to your existing incident model:

```python
# Add to existing Incident model:
investigation_run_id    = Column(UUID, ForeignKey("investigation_runs.id"), nullable=False)
related_event_ids       = Column(JSONB, nullable=False, default=[])
related_sources         = Column(JSONB, nullable=False, default=[])
# related_sources: ["sensor", "access"] — which source tables contributed
cluster_centroid_lat    = Column(Numeric(10, 7))
cluster_centroid_lon    = Column(Numeric(10, 7))
confidence_score        = Column(Numeric(4, 3), nullable=False)
# confidence_score: 0.000 to 1.000
confidence_level        = Column(String(16), nullable=False)
# confidence_level: low | medium | high
recommended_action      = Column(String(64), nullable=False)
# recommended_action: none | monitor | notify_supervisor | review_footage
reasoning_trace         = Column(JSONB, nullable=False, default=[])
# reasoning_trace: full list of messages exchanged with Groq
tool_calls_made         = Column(JSONB, nullable=False, default=[])
# tool_calls_made: [{tool, args, result_summary}] ordered list
triggered_by            = Column(String(64), default="scheduled")
# triggered_by: scheduled | incident_hook | manual
original_confidence     = Column(Numeric(4, 3))
# original_confidence: set when human overrides — preserves what agent said
```

---

## 2. Data Services Layer — NEW DIRECTORY

**Create: `app/data_services/`**

These are internal Python classes. They are never imported by routers.
They are never called by the agent. Only MCP handlers call them.
One service per source table.

---

### 2.1 `data_services/sensor_service.py`

```python
class SensorService:
    def __init__(self, db: Session):
        self.db = db

    def get_for_window(
        self,
        site_id: str,
        start: datetime,
        end: datetime,
        zone: str = None,
        sensor_type: str = None,
        breached_only: bool = False
    ) -> dict:
        """
        Queries sensor_readings with the provided filters.
        Always uses the (site_id, recorded_at) index.
        Returns a structured dict, never raw ORM objects.

        Return shape:
        {
          "available": bool,
          "count": int,
          "events": [
            {
              "id": str,
              "recorded_at": ISO8601,
              "zone": str,
              "sensor_type": str,
              "raw_value": float,
              "threshold_breached": bool,
              "lat": float,
              "lon": float
            }
          ],
          "breached_count": int,
          "zones_affected": [str]
        }
        """

    def get_by_ids(self, ids: list[str]) -> dict:
        """Fetch specific events by UUID list. Used for incident cross-reference."""
```

---

### 2.2 `data_services/access_service.py`

```python
class AccessService:
    def __init__(self, db: Session):
        self.db = db

    def get_for_window(
        self,
        site_id: str,
        start: datetime,
        end: datetime,
        gate_id: str = None,
        outcome_filter: str = None   # fail | forced | tailgate
    ) -> dict:
        """
        Return shape:
        {
          "available": bool,
          "count": int,
          "failed_count": int,
          "events": [
            {
              "id": str,
              "recorded_at": ISO8601,
              "gate_id": str,
              "zone": str,
              "badge_id": str,
              "outcome": str,
              "failure_reason": str,
              "lat": float,
              "lon": float
            }
          ],
          "gates_with_failures": [str],
          "consecutive_failures": int   # max consecutive fails on same gate
        }
        """
```

---

### 2.3 `data_services/vehicle_service.py`

```python
class VehicleService:
    def __init__(self, db: Session):
        self.db = db

    def get_for_window(
        self,
        site_id: str,
        start: datetime,
        end: datetime,
        zone: str = None,
        restricted_only: bool = False,
        path_segment_id: str = None
    ) -> dict:
        """
        Return shape:
        {
          "available": bool,
          "count": int,
          "restricted_zone_count": int,
          "unique_vehicles": int,
          "events": [...],
          "path_segments": [
            {
              "path_segment_id": str,
              "vehicle_id": str,
              "start_time": ISO8601,
              "end_time": ISO8601,
              "points": [{lat, lon, recorded_at, speed_kmh}],
              "entered_restricted": bool,
              "zones_traversed": [str]
            }
          ]
        }
        """
        # path reconstruction: group by path_segment_id, order by recorded_at ASC
        # this is the key value-add — raw rows become structured paths
```

---

### 2.4 `data_services/drone_service.py`

```python
class DroneService:
    def __init__(self, db: Session):
        self.db = db

    def get_for_window(
        self,
        site_id: str,
        mission_id: str = None,
        start: datetime = None,
        end: datetime = None,
        flagged_only: bool = False
    ) -> dict:
        """
        Return shape:
        {
          "available": bool,
          "missions": [
            {
              "mission_id": str,
              "mission_type": str,
              "drone_id": str,
              "start_time": ISO8601,
              "end_time": ISO8601,
              "waypoint_count": int,
              "flagged_count": int,
              "path_geojson": {...},   # GeoJSON LineString
              "waypoints": [
                {
                  "index": int,
                  "lat": float,
                  "lon": float,
                  "recorded_at": ISO8601,
                  "observation": str,
                  "flagged": bool,
                  "flag_reason": str
                }
              ]
            }
          ]
        }
        """
```

---

### 2.5 `data_services/weather_service.py`

```python
class WeatherService:
    def __init__(self, db: Session):
        self.db = db

    def get_for_window(self, site_id: str, start: datetime, end: datetime) -> dict:
        """
        CRITICAL: Returns per-15-minute buckets, not just aggregates.
        The agent must have granular readings to avoid coarse-data errors.

        Return shape:
        {
          "available": bool,
          "window_start": ISO8601,
          "window_end": ISO8601,
          "readings_count": int,
          "max_wind_kmh": float,
          "min_visibility_m": float,
          "above_fence_threshold": bool,   # True if max_wind > 28 km/h
          "severity_label": str,           # calm | moderate | strong | severe
          "precipitation": str,
          "readings_by_15min": [
            {
              "bucket_start": ISO8601,
              "wind_kmh": float,
              "gust_kmh": float,
              "precipitation": str,
              "visibility_m": float
            }
          ]
        }
        """

    def _wind_severity(self, wind_kmh: float) -> str:
        if wind_kmh < 15: return "calm"
        if wind_kmh < 28: return "moderate"
        if wind_kmh < 45: return "strong"
        return "severe"

    def _bucket_by_15min(self, rows: list) -> list:
        # groups readings into 15-minute buckets
        # returns list ordered by bucket_start ASC
        ...
```

---

### 2.6 `data_services/site_service.py`

```python
class SiteService:
    def __init__(self, db: Session):
        self.db = db

    def get_zone(self, site_id: str, zone_id: str = None) -> dict:
        """
        Return shape:
        {
          "available": bool,
          "zones": [
            {
              "zone_id": str,
              "zone_name": str,
              "zone_type": str,
              "is_restricted": bool,
              "access_rules": {
                "allowed_roles": [str],
                "allowed_hours": str,       # e.g. "06:00-22:00"
                "requires_escort": bool
              },
              "expected_vehicles": bool,
              "boundary_geojson": {...}
            }
          ]
        }
        """

    def get_shift(self, site_id: str, date: str) -> dict:
        """
        Return shape:
        {
          "available": bool,
          "shift_type": str,
          "shift_start": ISO8601,
          "shift_end": ISO8601,
          "supervisor_id": str,
          "headcount": int,
          "active_zones": [str],
          "scheduled_maintenance": [
            {"zone": str, "description": str, "start": ISO8601, "end": ISO8601}
          ],
          "is_overnight": bool,
          "reduced_staffing": bool   # True if headcount < normal threshold
        }
        """
```

---

### 2.7 `data_services/historical_service.py`

```python
class HistoricalService:
    def __init__(self, db: Session):
        self.db = db

    def get_patterns(
        self,
        site_id: str,
        event_type: str,
        zone: str,
        lookback_days: int = 30
    ) -> dict:
        """
        Queries the source tables for similar events over the lookback window.
        Returns frequency, typical characteristics, and anomaly indicator.

        Return shape:
        {
          "available": bool,
          "lookback_days": int,
          "event_type": str,
          "zone": str,
          "occurrence_count": int,
          "avg_per_night": float,
          "typical_time_range": str,   # e.g. "01:00-03:00"
          "is_anomalous": bool,        # True if current event is unusual vs history
          "last_similar_event": ISO8601
        }
        """
        # MVP: query current source tables for historical data
        # Post-MVP: dedicated time-series store or materialized view
```

---

## 3. MCP Server Layer — NEW DIRECTORY

**Create: `app/mcp_server/`**

The MCP server is a separate process from FastAPI. In development it runs
via stdio. In production it runs as an SSE HTTP server on port 8001.

---

### 3.1 `mcp_server/server.py`

The entry point. Instantiates the MCP server and registers all 10 tools.
Each `@server.tool()` decorated function receives validated, typed args from
the MCP framework and delegates to the corresponding handler.

Tool registration order:
1. `retrieveSensorEvents`
2. `retrieveAccessLogs`
3. `retrieveVehicleEvents`
4. `retrieveDroneLogs`
5. `getWeatherContext`
6. `getShiftSchedule`
7. `getSiteMetadata`
8. `getHistoricalPatterns`
9. `clusterEventsByLocation`
10. `simulateDroneInspection`

Each tool function signature must exactly match what the Groq tool schema
in `agent/prompts.py` declares. If they diverge the agent will emit args
the handler rejects.

---

### 3.2 `mcp_server/transport_stdio.py`

Used in local development. The MCP client in the orchestrator spawns the
server as a subprocess and communicates over stdin/stdout pipes.

```python
# Entry point for stdio mode:
if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    asyncio.run(stdio_server(server))
```

---

### 3.3 `mcp_server/transport_sse.py`

Used in production. Runs the MCP server as an HTTP server with SSE endpoint.
The orchestrator connects as an HTTP client. FastAPI is on port 8000,
MCP server is on port 8001.

```python
# Entry point for SSE mode:
if __name__ == "__main__":
    import uvicorn
    from mcp.server.sse import SseServerTransport
    transport = SseServerTransport("/mcp/sse")
    uvicorn.run(transport.get_app(server), host="0.0.0.0", port=8001)
```

Set via env: `MCP_TRANSPORT=sse` (production) or `MCP_TRANSPORT=stdio` (dev).

---

### 3.4 Handler Files — `mcp_server/handlers/`

One file per tool. Each handler follows the same contract:

1. Receives validated, typed params from the MCP server
2. Opens a DB session
3. Instantiates the appropriate data service
4. Calls the service method
5. Returns a dict
6. Never raises exceptions — catches internally, returns `{"available": false, "error": "..."}`

**`handlers/sensor_handler.py`**
```python
async def fetch(site_id, start_time, end_time, zone, sensor_type, breached_only):
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        with get_session() as db:
            return SensorService(db).get_for_window(
                site_id, start, end, zone, sensor_type, breached_only
            )
    except Exception as e:
        return {"available": False, "error": str(e)}
```

Same pattern for: `access_handler.py`, `vehicle_handler.py`,
`drone_handler.py`, `weather_handler.py`, `shift_handler.py`,
`site_metadata_handler.py`, `historical_handler.py`.

**`handlers/spatial_handler.py`** — calls DBSCAN logic from `tools/spatial_tools.py`.
This is the one handler that does not need a DB session — it operates purely
on the event list passed in.

```python
async def cluster(events: list) -> dict:
    """
    Input: list of {id, lat, lon, timestamp, source}
    Runs DBSCAN with epsilon=200m (haversine distance), min_samples=1.
    Returns:
    {
      "cluster_count": int,
      "noise_count": int,     # events DBSCAN labeled as noise (-1)
      "clusters": [
        {
          "cluster_id": int,
          "centroid_lat": float,
          "centroid_lon": float,
          "event_count": int,
          "source_diversity": int,   # number of distinct source tables
          "time_span_minutes": float,
          "events": [...]            # full event dicts
        }
      ]
    }
    """
```

**`handlers/drone_simulate_handler.py`** — generates a simulated drone path
and persists a `DroneMission` record.

```python
async def simulate(site_id, incident_id, target_lat, target_lon, radius_m):
    """
    Generates a realistic patrol path around target_lat/lon within radius_m.
    Creates waypoints with synthetic observations.
    Persists to drone_missions table (not drone_telemetry — that is source data).
    Returns:
    {
      "mission_id": str,
      "path_geojson": {...},     # GeoJSON LineString
      "waypoints": [
        {
          "index": int,
          "lat": float,
          "lon": float,
          "observation": str,
          "flagged": bool
        }
      ],
      "findings_summary": str
    }
    """
```

---

## 4. Orchestrator Changes — MODIFY `agent/orchestrator.py`

Your existing orchestrator calls tools directly as Python functions.
It needs to route all tool calls through the MCP client instead.

### 4.1 Add `call_mcp_tool()` function

```python
async def call_mcp_tool(tool_name: str, args: dict) -> dict:
    """
    Routes a tool call to the MCP server.
    In dev (MCP_TRANSPORT=stdio): spawns MCP server subprocess, calls over pipes.
    In prod (MCP_TRANSPORT=sse): calls MCP server over HTTP SSE on port 8001.
    """
    if settings.MCP_TRANSPORT == "stdio":
        return await _call_via_stdio(tool_name, args)
    else:
        return await _call_via_sse(tool_name, args)
```

### 4.2 Add `fetch_all_events_for_window()` — orchestrator-level DB query

This is the one place the orchestrator touches the DB directly.
It queries all source tables to build the initial event list for clustering.
It does NOT go through MCP — this is a broad fan-out read, not a scoped
context fetch.

```python
def fetch_all_events_for_window(
    db: Session,
    site_id: str,
    window_start: datetime,
    window_end: datetime,
    source_filter: list = None,
    zone_filter: str = None
) -> list:
    """
    Queries sensor_readings, access_events, vehicle_detections, drone_telemetry.
    Weather and site_metadata are NOT included — they are context, not events.
    Returns unified list: [{id, source, timestamp, lat, lon, zone, type, flagged}]
    Applies source_filter and zone_filter when provided (used by hook-triggered runs).
    """
```

### 4.3 Modify the investigation loop

```python
async def investigate_cluster(cluster: dict, run: InvestigationRun, db: Session):
    messages = [build_cluster_message(cluster)]
    tools = get_tool_schemas()
    tool_calls_log = []

    while True:
        response = groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=2048
        )
        choice = response.choices[0]

        if choice.finish_reason == "stop":
            parsed = parse_incident_response(choice.message.content)
            confidence = score_confidence(
                signal_count=len(cluster["events"]),
                source_diversity=len(set(e["source"] for e in cluster["events"])),
                context_alignment=parsed.get("context_alignment_score", 0.5),
                uncertainty_language=parsed.get("uncertainty_language", False)
            )
            return build_incident(parsed, confidence, cluster, run, tool_calls_log, messages)

        messages.append(choice.message)

        for tc in choice.message.tool_calls:
            # ROUTE THROUGH MCP — not direct function call
            result = await call_mcp_tool(
                tc.function.name,
                json.loads(tc.function.arguments)
            )
            tool_calls_log.append({
                "tool": tc.function.name,
                "args": json.loads(tc.function.arguments),
                "result_summary": str(result)[:200]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result)
            })
```

---

## 5. Hook Service — NEW

**Create: `services/hook_service.py`**

```python
class HookService:

    async def process_hook(self, hook_id: str, db: Session):
        """
        Full lifecycle for an incident hook:
        1. Load hook record, set status = processing
        2. Compute time window: now() - lookback_minutes → now()
        3. Create InvestigationRun with trigger_type = "incident_hook"
        4. Call run_investigation_with_context() with:
           - extra_context dict containing hook observation, notes, severity_hint
           - source_filter from hook.include_sources
           - zone_filter from hook.zone
        5. On completion: set hook.status = complete, hook.incident_id if created
        6. On failure: set hook.status = failed, hook.error_message
        """

    def _build_hook_context_prompt(self, hook: HookEvent) -> str:
        """
        Returns a string injected at the top of the agent system prompt
        for hook-triggered runs:

        OPERATOR OBSERVATION (submitted by {submitted_by}):
        "{observation}"

        OPERATOR NOTES: "{notes}"
        SEVERITY HINT: {severity_hint}
        ZONE FOCUS: {zone}

        You are investigating this specific observation.
        Prioritise signals from the {zone} zone in the last {lookback_minutes} minutes.
        The operator's observation is not evidence — it is context.
        Let the signals lead you.
        """
```

---

## 6. Hook Router — NEW `routers/hooks.py`

```python
POST   /api/v1/hooks/incident
       Body: HookRequest schema (see schemas/hooks.py)
       Returns: {hook_id, run_id, status, poll_url}
       Action: Creates HookEvent, queues BackgroundTask → hook_service.process_hook()

GET    /api/v1/hooks/incident/{hook_id}/status
       Returns: {hook_id, status, run_id, incident_id, incident_summary}
       incident_summary only present when status = complete

GET    /api/v1/hooks/incident
       Returns: paginated list of all hooks with run_id and incident_id
       Query params: submitted_by, status, date
```

### `schemas/hooks.py`

```python
class HookRequest(BaseModel):
    site_id: str
    submitted_by: str
    observation: str
    zone: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    severity_hint: Optional[Literal["low", "medium", "high"]] = None
    lookback_minutes: int = 120
    include_sources: Optional[list[str]] = None
    # defaults to all: ["sensor", "access", "vehicle", "drone", "weather"]
    notes: Optional[str] = None

class HookResponse(BaseModel):
    hook_id: str
    run_id: str
    status: str
    estimated_completion_seconds: int
    poll_url: str

class HookStatusResponse(BaseModel):
    hook_id: str
    status: str
    run_id: Optional[str]
    incident_id: Optional[str]
    incident_summary: Optional[dict]  # hypothesis, confidence_level, recommended_action
```

---

## 7. Debug Endpoints — NEW `routers/tools_debug.py`

These exist so engineers can call MCP tools directly during development
without running a full investigation. Essential for verifying tool output.

```python
GET  /api/v1/tools/sensor
     Params: site_id, start, end, zone, breached_only
     Calls: retrieveSensorEvents via MCP, returns raw result

GET  /api/v1/tools/access
     Params: site_id, start, end, gate_id, outcome_filter

GET  /api/v1/tools/vehicle
     Params: site_id, start, end, zone, restricted_only

GET  /api/v1/tools/drone
     Params: site_id, mission_id, start, end, flagged_only

GET  /api/v1/tools/weather
     Params: site_id, start, end

GET  /api/v1/tools/shift
     Params: site_id, date

GET  /api/v1/tools/site
     Params: site_id, zone
```

All return the raw dict the MCP handler returns. Useful for checking that
weather returns `readings_by_15min`, vehicle returns reconstructed paths, etc.

---

## 8. Seed Script Changes — MODIFY `seed/`

Your existing seed script needs to be updated to populate all six source
tables, not a single events table.

### `seed/scenarios/block_c_incident.py`

Must seed across all tables:

**sensor_readings** (4 rows)
- fence_vibration at Gate 3, zone=gate-3, 01:12, threshold_breached=True
- motion sensor near Block C storage, 01:08, threshold_breached=True
- motion sensor near Block C storage, 01:31, threshold_breached=False
- perimeter alert, zone=block-c, 01:19

**access_events** (3 rows)
- badge fail, gate=access-point-7, zone=block-c, 01:15, failure_reason=after_hours
- badge fail, gate=access-point-7, zone=block-c, 01:17, failure_reason=after_hours
- badge fail, gate=access-point-7, zone=block-c, 01:22, failure_reason=unknown_badge

**vehicle_detections** (8-10 rows, same path_segment_id)
- vehicle_id=VH-041, path from 01:08 to 01:31
- path enters zone=block-c at 01:11, in_restricted=True from 01:14-01:22
- all rows share path_segment_id="seg-20260418-001"

**drone_telemetry** (12-15 rows, mission_id="mission-20260418-01")
- scheduled patrol, drone_id=DRONE-2
- covers gate-3 zone at 01:45-01:52
- covers block-c zone at 02:00-02:18
- 2 flagged waypoints in block-c zone with observation text

**weather_readings** (24 rows — one per 15 minutes from 22:00 to 06:00)
- wind 28-36 km/h during 00:00-02:00
- wind 10-14 km/h during 02:30-06:00 (calm period)
- This is critical — the agent must see that wind was calm at 01:12,
  NOT just a high overnight average

**site_zones** (6 rows)
- gate-3: is_restricted=False, expected_vehicles=False
- block-c: is_restricted=True, expected_vehicles=False
- block-c-storage: is_restricted=True, expected_vehicles=False
- main-yard: is_restricted=False, expected_vehicles=True
- access-point-7: is_restricted=False
- perimeter: is_restricted=False

**shift_schedule** (1 row)
- night shift 22:00-06:00
- headcount=4
- active_zones=[main-yard, perimeter]
- block-c NOT in active_zones (makes badge fails more suspicious)

**Noise events** (8-10 rows across tables)
- 2 successful badge swipes at main entrance 23:30, 00:45
- 1 forklift in main-yard (expected, in_restricted=False) 23:45
- 1 scheduled calibration sensor reading 01:00
- 1 drone waypoint in main-yard with no observation (routine)

---

## 9. `config.py` — Add MCP Settings

```python
class Settings(BaseSettings):
    # existing settings...

    # MCP
    MCP_TRANSPORT: str = "stdio"           # stdio | sse
    MCP_SERVER_HOST: str = "localhost"
    MCP_SERVER_PORT: int = 8001

    # Site
    SITE_ID: str = "ridgeway-01"
    INVESTIGATION_WINDOW_HOURS: int = 8    # how far back a scheduled run looks

    # Hook defaults
    HOOK_DEFAULT_LOOKBACK_MINUTES: int = 120
    HOOK_MAX_LOOKBACK_MINUTES: int = 480
```

---

## 10. What to Leave Alone

| File | Status |
|---|---|
| `app/main.py` | Keep — add hook router registration |
| `app/database.py` | Keep — no changes needed |
| `agent/confidence.py` | Keep — expand with uncertainty_language param |
| `agent/prompts.py` | Keep — add tool schemas for all 10 tools, expand system prompt |
| `tools/spatial_tools.py` | Keep — becomes the implementation called by spatial_handler.py |
| `tools/drone_tools.py` | Keep — becomes the implementation called by drone_simulate_handler.py |
| `tools/signal_tools.py` | Replace with data_services + MCP handlers |
| `tools/context_tools.py` | Replace with data_services + MCP handlers |
| `models/event.py` | Replace with 6 source table models |
| `routers/investigate.py` | Keep — add run_id to response |
| `routers/incidents.py` | Keep — add challenge endpoint if missing |
