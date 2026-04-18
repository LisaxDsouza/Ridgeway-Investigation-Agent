from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..models.weather_readings import WeatherReading

class WeatherService:
    def __init__(self, db: Session):
        self.db = db

    def get_for_window(self, site_id: str, start: datetime, end: datetime) -> dict:
        readings = self.db.query(WeatherReading).filter(
            WeatherReading.site_id == site_id,
            WeatherReading.recorded_at >= start,
            WeatherReading.recorded_at <= end
        ).order_by(WeatherReading.recorded_at.asc()).all()

        if not readings:
            return {"available": False}

        max_wind = max(float(r.wind_kmh) for r in readings if r.wind_kmh is not None)
        min_visibility = min(float(r.visibility_m) for r in readings if r.visibility_m is not None)

        return {
            "available": True,
            "window_start": start.isoformat(),
            "window_end": end.isoformat(),
            "readings_count": len(readings),
            "max_wind_kmh": max_wind,
            "min_visibility_m": min_visibility,
            "above_fence_threshold": max_wind > 28,  # Heuristic for wind-induced false positives
            "severity_label": self._wind_severity(max_wind),
            "precipitation": readings[0].precipitation, # Simplification for MVP
            "readings_by_15min": self._bucket_by_15min(readings)
        }

    def _wind_severity(self, wind_kmh: float) -> str:
        if wind_kmh < 15: return "calm"
        if wind_kmh < 28: return "moderate"
        if wind_kmh < 45: return "strong"
        return "severe"

    def _bucket_by_15min(self, rows: list) -> list:
        # Group into 15m buckets
        buckets = []
        for r in rows:
            buckets.append({
                "bucket_start": r.recorded_at.isoformat(),
                "wind_kmh": float(r.wind_kmh) if r.wind_kmh else 0,
                "gust_kmh": float(r.gust_kmh) if r.gust_kmh else 0,
                "precipitation": r.precipitation,
                "visibility_m": float(r.visibility_m) if r.visibility_m else 0
            })
        return buckets
