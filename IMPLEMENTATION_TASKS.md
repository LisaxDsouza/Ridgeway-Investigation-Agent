# Implementation Task List
## ridgeway-intelligence / backend
### Ordered by dependency — do not skip ahead

---

## PHASE 0 — Before Writing Any Code

- [ ] Read `BACKEND_SERVICES.md` in full
- [ ] Confirm `GROQ_API_KEY` works — call the Groq API once manually
- [ ] Confirm PostgreSQL is running and `DATABASE_URL` connects
- [ ] Add to `config.py`: `MCP_TRANSPORT`, `MCP_SERVER_HOST`, `MCP_SERVER_PORT`, `SITE_ID`, `INVESTIGATION_WINDOW_HOURS`, `HOOK_DEFAULT_LOOKBACK_MINUTES`
- [ ] Install new dependencies: `mcp`, `scikit-learn`, `numpy`, `groq` — add to `requirements.txt`

---

## PHASE 1 — Database Models + Migrations

Work bottom-up. Every model must exist before seeding or querying.

- [ ] **1.1** Delete `models/event.py` — it will be replaced
- [ ] **1.2** Create `models/sensor_readings.py` with `SensorReading` class and all column definitions
- [ ] **1.3** Create `models/access_events.py` with `AccessEvent` class
- [ ] **1.4** Create `models/vehicle_detections.py` with `VehicleDetection` class
- [ ] **1.5** Create `models/drone_telemetry.py` with `DroneTelemetry` class (distinct from `drone_mission.py`)
- [ ] **1.6** Create `models/weather_readings.py` with `WeatherReading` class
- [ ] **1.7** Create `models/site_metadata.py` with `SiteZone` and `ShiftSchedule` classes
- [ ] **1.8** Create `models/investigation_runs.py` with `InvestigationRun` class
- [ ] **1.9** Create `models/hook_events.py` with `HookEvent` class
- [ ] **1.10** Expand `models/incident.py` — add all new fields listed in section 1.9 of services doc
- [ ] **1.11** Update `models/__init__.py` to export all new models
- [ ] **1.12** Run `alembic revision --autogenerate -m "source_tables_and_system_tables"`
- [ ] **1.13** Run `alembic upgrade head`
- [ ] **1.14** Verify all tables created: `\dt` in psql — expect 12+ tables
- [ ] **1.15** Add all indexes manually in a second migration (Alembic won't generate partial indexes) — `alembic revision -m "add_source_table_indexes"`

---

## PHASE 2 — Seed Script

Seed before writing services so you have real data to query against.

- [ ] **2.1** Rewrite `seed/scenarios/block_c_incident.py` to populate all 6 source tables
- [ ] **2.2** Seed `sensor_readings` — 4 rows including Gate 3 fence vibration at 01:12
- [ ] **2.3** Seed `access_events` — 3 failed badge swipes at access-point-7, zone=block-c
- [ ] **2.4** Seed `vehicle_detections` — 8-10 rows sharing `path_segment_id`, vehicle in restricted zone
- [ ] **2.5** Seed `drone_telemetry` — 12-15 rows, scheduled mission, 2 flagged waypoints
- [ ] **2.6** Seed `weather_readings` — **24 rows at 15-min intervals** from 22:00-06:00. Wind high 00:00-02:00, calm 02:30+. This is critical.
- [ ] **2.7** Seed `site_zones` — 6 zones including block-c as restricted
- [ ] **2.8** Seed `shift_schedule` — night shift, block-c NOT in active_zones
- [ ] **2.9** Seed noise events — 8-10 rows across tables (routine vehicle, successful badges, calibration)
- [ ] **2.10** Run `python seed/seed.py` and verify row counts in each table

---

## PHASE 3 — Data Services

One service per source table. No skipping. These are tested independently
before MCP handlers are written.

- [ ] **3.1** Create `data_services/` directory with `__init__.py`
- [ ] **3.2** Create `data_services/sensor_service.py` — `get_for_window()` and `get_by_ids()`
- [ ] **3.3** Create `data_services/access_service.py` — `get_for_window()` with consecutive_failures calculation
- [ ] **3.4** Create `data_services/vehicle_service.py` — `get_for_window()` with path reconstruction by `path_segment_id`
- [ ] **3.5** Create `data_services/drone_service.py` — `get_for_window()` with GeoJSON path construction
- [ ] **3.6** Create `data_services/weather_service.py` — `get_for_window()` with `_bucket_by_15min()` method
- [ ] **3.7** Create `data_services/site_service.py` — `get_zone()` and `get_shift()` with `is_overnight` and `reduced_staffing` derived fields
- [ ] **3.8** Create `data_services/historical_service.py` — `get_patterns()` with anomaly detection
- [ ] **3.9** Test each service directly in a Python shell against seeded data:
  - `SensorService(db).get_for_window("ridgeway-01", ...)` → expect 4 events
  - `WeatherService(db).get_for_window(...)` → expect `readings_by_15min` with 24 buckets
  - `VehicleService(db).get_for_window(...)` → expect reconstructed path, `entered_restricted=True`

---

## PHASE 4 — MCP Server

The MCP server is what turns plain Python functions into agent-callable tools.
Build this after data services are verified.

- [ ] **4.1** Create `mcp_server/` directory with `__init__.py`
- [ ] **4.2** Create `mcp_server/handlers/` directory with `__init__.py`
- [ ] **4.3** Create `mcp_server/handlers/sensor_handler.py` — calls `SensorService`
- [ ] **4.4** Create `mcp_server/handlers/access_handler.py` — calls `AccessService`
- [ ] **4.5** Create `mcp_server/handlers/vehicle_handler.py` — calls `VehicleService`
- [ ] **4.6** Create `mcp_server/handlers/drone_handler.py` — calls `DroneService`
- [ ] **4.7** Create `mcp_server/handlers/weather_handler.py` — calls `WeatherService`
- [ ] **4.8** Create `mcp_server/handlers/shift_handler.py` — calls `SiteService.get_shift()`
- [ ] **4.9** Create `mcp_server/handlers/site_metadata_handler.py` — calls `SiteService.get_zone()`
- [ ] **4.10** Create `mcp_server/handlers/historical_handler.py` — calls `HistoricalService`
- [ ] **4.11** Create `mcp_server/handlers/spatial_handler.py` — calls DBSCAN logic from `tools/spatial_tools.py`, returns structured cluster dict
- [ ] **4.12** Create `mcp_server/handlers/drone_simulate_handler.py` — generates path, persists `DroneMission`, returns GeoJSON
- [ ] **4.13** Create `mcp_server/server.py` — instantiate `Server("ridgeway-site-tools")`, register all 10 tools with `@server.tool()` decorators
- [ ] **4.14** Create `mcp_server/transport_stdio.py` — stdio entry point for dev
- [ ] **4.15** Create `mcp_server/transport_sse.py` — SSE HTTP entry point for prod
- [ ] **4.16** Test MCP server manually:
  - Start: `python mcp_server/transport_stdio.py`
  - In a second terminal, call it with the MCP client — verify all 10 tools are registered
  - Call `getWeatherContext` directly — verify it returns `readings_by_15min`
  - Call `clusterEventsByLocation` with the seeded event list — verify clusters returned

---

## PHASE 5 — Agent Orchestrator Wiring

Now connect the agent to MCP. Your existing orchestrator logic is mostly right
but currently calls tools as direct Python functions.

- [ ] **5.1** Update `agent/prompts.py` — write tool JSON schemas for all 10 tools. Each schema must exactly match the parameter names in `mcp_server/server.py`. Add these instructions to the system prompt:
  - Always call `getWeatherContext` when `fence_vibration` is in cluster
  - Always call `getShiftSchedule` when failed badge events present
  - Always call `getSiteMetadata` for clusters near restricted zones
  - Output ONLY valid JSON when done — no prose
- [ ] **5.2** Add `call_mcp_tool(tool_name, args)` to `agent/orchestrator.py` — routes via stdio (dev) or SSE (prod) based on `settings.MCP_TRANSPORT`
- [ ] **5.3** Add `fetch_all_events_for_window(db, site_id, start, end, source_filter, zone_filter)` to orchestrator — queries all 4 event source tables directly (this is the one legitimate direct DB call in the orchestrator)
- [ ] **5.4** Update `agent/confidence.py` — add `uncertainty_language: bool` parameter, apply 0.75 multiplier when True
- [ ] **5.5** Update orchestrator investigation loop — replace direct tool function calls with `await call_mcp_tool(...)`
- [ ] **5.6** Add `tool_calls_made` logging inside the loop — capture tool name, args, result summary for each call
- [ ] **5.7** Add `InvestigationRun` creation and status updates to `run_investigation()`
- [ ] **5.8** End-to-end test — no frontend needed:
  - Start MCP server: `python mcp_server/transport_stdio.py`
  - Run: `python -c "from app.agent.orchestrator import run_investigation; ..."`
  - Verify `GET /api/v1/incidents` returns incidents with `reasoning_trace` and `tool_calls_made` populated
  - Verify at least one incident has `triggered_by = scheduled`

---

## PHASE 6 — Incident Hook

- [ ] **6.1** Create `schemas/hooks.py` — `HookRequest`, `HookResponse`, `HookStatusResponse`
- [ ] **6.2** Create `services/hook_service.py` — `process_hook()` and `_build_hook_context_prompt()`
- [ ] **6.3** Create `routers/hooks.py` — three endpoints: POST submit, GET status, GET list
- [ ] **6.4** Register `hooks` router in `main.py`
- [ ] **6.5** Update `run_investigation()` to accept `extra_context` dict — when present, prepend hook context to system prompt
- [ ] **6.6** Test hook end-to-end:
  - `POST /api/v1/hooks/incident` with observation about Block C
  - Poll `GET /api/v1/hooks/incident/{hook_id}/status` every 2 seconds
  - Verify status transitions: queued → processing → complete
  - Verify returned `incident_id` exists in database with `triggered_by = "incident_hook"`
  - Verify the incident's `tool_calls_made` shows zone-filtered tool calls

---

## PHASE 7 — Remaining API Endpoints

These are straightforward after the core is working.

- [ ] **7.1** `GET /api/v1/events` — queries all source tables, returns unified list. Query params: `source`, `zone`, `start`, `end`
- [ ] **7.2** `GET /api/v1/events/{id}` — queries the correct source table based on event type, returns single event + linked incident_id
- [ ] **7.3** `GET /api/v1/investigate/{run_id}/result` — full result with events_fetched, clusters_found, incidents_created
- [ ] **7.4** `POST /api/v1/incidents/{id}/challenge` — re-run agent loop with challenge_text injected into system prompt, update incident with new hypothesis + original_confidence preserved
- [ ] **7.5** `GET /api/v1/briefing` — assemble from accepted incidents, generate if not yet created
- [ ] **7.6** `POST /api/v1/briefing/export`
- [ ] **7.7** `GET /api/v1/drone/missions`
- [ ] **7.8** `POST /api/v1/drone/simulate`

---

## PHASE 8 — Debug Tool Endpoints

- [ ] **8.1** Create `routers/tools_debug.py` with 7 GET endpoints (sensor, access, vehicle, drone, weather, shift, site)
- [ ] **8.2** Each endpoint calls `call_mcp_tool()` directly with query params as args
- [ ] **8.3** Register `tools_debug` router in `main.py`
- [ ] **8.4** Verify each endpoint manually — confirm weather returns `readings_by_15min`, vehicle returns `path_segments`

---

## PHASE 9 — Briefing Service

- [ ] **9.1** Create `services/briefing_service.py` — accepts list of accepted incidents, calls Groq once to generate five-question briefing text
- [ ] **9.2** Briefing system prompt must map explicitly to five questions:
  - Q1: what actually happened last night
  - Q2: what was harmless
  - Q3: what deserves escalation
  - Q4: what did the drone check
  - Q5: what still needs follow-up
- [ ] **9.3** Persist `Briefing` row with all five question fields + `export_text`

---

## PHASE 10 — Chat Endpoint

- [ ] **10.1** Create `services/chat_service.py` — fetches current incidents + events, builds scoped context, calls Groq with streaming
- [ ] **10.2** System prompt for chat: "Answer only from the provided incident and event data. If you cannot ground your answer in this data, say so. Do not speculate."
- [ ] **10.3** `POST /api/v1/chat` — streaming SSE. Body: `{message, conversation_history}`
- [ ] **10.4** Test 5 key questions:
  - "What happened near Block C?"
  - "Why did the drone go there?"
  - "What should I escalate?"
  - "Was Gate 3 a real threat?"
  - "Give me a summary of last night"

---

## PHASE 11 — Final Verification Before Frontend Handoff

Run these checks before telling the frontend team the backend is ready.

- [ ] `POST /api/v1/investigate` → incidents created with non-empty `reasoning_trace`
- [ ] `GET /api/v1/incidents` returns at least 3 incidents from Block C scenario
- [ ] At least one incident has `confidence_level = low` or `medium` (not all high — that means uncertainty isn't working)
- [ ] At least one incident has `tool_calls_made` showing 3+ different tools called
- [ ] `GET /api/v1/tools/weather` returns `readings_by_15min` array with multiple entries
- [ ] `GET /api/v1/tools/vehicle` returns `path_segments` with `entered_restricted = true`
- [ ] `POST /api/v1/hooks/incident` triggers a new run, returns an incident within 20 seconds
- [ ] `GET /api/v1/briefing` returns all five question fields populated
- [ ] All 10 MCP tools appear in `python mcp_server/server.py --list-tools` (or equivalent)

---

## Files to Delete

| File | Why |
|---|---|
| `models/event.py` | Replaced by 6 source-specific models |
| Any direct DB call inside `tools/signal_tools.py` | Move to `data_services/`, keep DBSCAN and simulation logic |
| Any direct DB call inside `tools/context_tools.py` | Move to `data_services/` |

---

## Files to Rename / Move

| Current | New location | Why |
|---|---|---|
| `tools/spatial_tools.py` | Keep in `tools/` — called by `mcp_server/handlers/spatial_handler.py` | Spatial logic stays, MCP handler wraps it |
| `tools/drone_tools.py` | Keep in `tools/` — called by `mcp_server/handlers/drone_simulate_handler.py` | Drone simulation logic stays, MCP handler wraps it |
