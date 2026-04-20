from mcp.server.fastmcp import FastMCP
from typing import List, Optional
from datetime import datetime
from ..database import SessionLocal
from .handlers import (
    sensor_handler,
    access_handler,
    vehicle_handler,
    drone_handler,
    weather_handler,
    shift_handler,
    site_metadata_handler,
    historical_handler,
    spatial_handler
)

mcp = FastMCP("Skylark-Forensics-Server")

@mcp.tool()
async def retrieveSensorEvents(
    site_id: str,
    start_time: str,
    end_time: str,
    zone: Optional[str] = None,
    sensor_type: Optional[str] = None,
    breached_only: bool = False
) -> dict:
    """Retrieve detailed sensor logs (vibration, perimeter, motion) for a time window."""
    return await sensor_handler.handle(site_id, start_time, end_time, zone, sensor_type, breached_only)

@mcp.tool()
async def retrieveAccessLogs(
    site_id: str,
    start_time: str,
    end_time: str,
    gate_id: Optional[str] = None,
    outcome_filter: Optional[str] = None
) -> dict:
    """Retrieve badge swipe and gate operation logs."""
    return await access_handler.handle(site_id, start_time, end_time, gate_id, outcome_filter)

@mcp.tool()
async def retrieveVehicleEvents(
    site_id: str,
    start_time: str,
    end_time: str,
    zone: Optional[str] = None,
    restricted_only: bool = False
) -> dict:
    """Retrieve vehicle detection events and reconstructed movement paths."""
    return await vehicle_handler.handle(site_id, start_time, end_time, zone, restricted_only)

@mcp.tool()
async def retrieveDroneLogs(
    site_id: str,
    start_time: str,
    end_time: str,
    mission_id: Optional[str] = None,
    flagged_only: bool = False
) -> dict:
    """Retrieve historical drone patrol telemetry and observations."""
    return await drone_handler.handle(site_id, start_time, end_time, mission_id, flagged_only)

@mcp.tool()
async def getWeatherContext(
    site_id: str,
    start_time: str,
    end_time: str
) -> dict:
    """Retrieve high-resolution 15-minute weather data (wind, visibility, precipitation)."""
    return await weather_handler.handle(site_id, start_time, end_time)

@mcp.tool()
async def getShiftSchedule(
    site_id: str,
    date: str
) -> dict:
    """Retrieve staff schedules, active zones, and maintenance windows for a specific date."""
    return await shift_handler.handle(site_id, date)

@mcp.tool()
async def getSiteMetadata(
    site_id: str,
    zone_id: Optional[str] = None
) -> dict:
    """Retrieve site layout, zone boundaries, and classification (restricted, storage, etc)."""
    return await site_metadata_handler.handle(site_id, zone_id)

@mcp.tool()
async def getHistoricalPatterns(
    site_id: str,
    event_type: str,
    zone: str,
    lookback_days: int = 30
) -> dict:
    """Compare current events against historical norms to detect anomalies."""
    return await historical_handler.handle(site_id, event_type, zone, lookback_days)

@mcp.tool()
async def clusterEventsByLocation(
    events: List[dict]
) -> dict:
    """Group a list of raw signals into discrete spatial clusters using DBSCAN."""
    return await spatial_handler.handle(events)
