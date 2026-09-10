"""
utils/weather_client.py — Free real-time weather & soil data client.

Uses the Open-Meteo APIs (no API key, no credit card, generous free tier):
  1. Geocoding API : village/city name → latitude / longitude
  2. Forecast API  : lat/lon → 7-day weather + SOIL data
                     (soil moisture, soil temperature) — perfect for farming!

If Grok is the "brain" of KisanMitra, this module is its "senses".
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import requests

import config

# Tiny in-memory cache so repeated dashboard refreshes don't hammer the API
_cache: Dict[str, tuple] = {}


def _is_fresh(key: str) -> bool:
    """Return True when a cached entry still lives inside the TTL window."""
    if key not in _cache:
        return False
    stored_at, _payload = _cache[key]
    return (time.time() - stored_at) < config.CACHE_TTL_MINUTES * 60


def geocode(place: str) -> Optional[Dict[str, Any]]:
    """Resolve a village/town/city name to coordinates via Open-Meteo.

    Returns the best match dict (name, admin1, country, latitude,
    longitude, elevation ...) or None when the place cannot be found.
    """
    key = f"geo:{place.strip().lower()}"
    if _is_fresh(key):
        return _cache[key][1]

    try:
        response = requests.get(
            config.GEOCODING_URL,
            params={"name": place.strip(), "count": 1, "language": "en"},
            timeout=config.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        results: List[Dict[str, Any]] = response.json().get("results") or []
    except (requests.RequestException, ValueError) as exc:
        print(f"[weather_client] geocoding failed for '{place}': {exc}")
        return None

    if not results:
        return None

    best = results[0]
    _cache[key] = (time.time(), best)
    return best


def fetch_agri_weather(latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
    """Fetch a farming-focused weather package for a location.

    Requested fields (all FREE on Open-Meteo):
      • weather_code, temperature_2m, relative_humidity_2m, precipitation,
        rain, wind_speed_10m  → general crop weather
      • soil_temperature_0cm, soil_moisture_0_to_7cm            → farm soil state
      • et0_fao_evapotranspiration                              → irrigation math
    """
    key = f"wx:{latitude:.3f},{longitude:.3f}"
    if _is_fresh(key):
        return _cache[key][1]

    try:
        response = requests.get(
            config.FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": ",".join(
                    [
                        "weather_code",
                        "temperature_2m",
                        "relative_humidity_2m",
                        "precipitation",
                        "wind_speed_10m",
                        "soil_temperature_0cm",
                        "soil_moisture_0_to_7cm",
                    ]
                ),
                "hourly": "temperature_2m,precipitation,relative_humidity_2m",
                "daily": ",".join(
                    [
                        "weather_code",
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "precipitation_sum",
                        "precipitation_probability_max",
                        "wind_speed_10m_max",
                        "et0_fao_evapotranspiration",
                    ]
                ),
                "timezone": "auto",
                "forecast_days": config.FORECAST_DAYS,
            },
            timeout=config.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        print(f"[weather_client] forecast fetch failed: {exc}")
        return None

    _cache[key] = (time.time(), payload)
    return payload


def get_farm_snapshot(place: str) -> Optional[Dict[str, Any]]:
    """One-call helper: place name → ready-to-use agri-weather snapshot.

    Combines geocoding + forecast fetch + derived helpers (rain risk,
    heat stress, soil state labels) into a single dict the agents reason over.
    """
    location = geocode(place)
    if not location:
        return None

    data = fetch_agri_weather(location["latitude"], location["longitude"])
    if not data:
        return None

    current = data.get("current", {})
    daily = data.get("daily", {})

    temp = float(current.get("temperature_2m") or 0)
    humidity = float(current.get("relative_humidity_2m") or 0)
    soil_moisture = float(current.get("soil_moisture_0_to_7cm") or 0)  # m³/m³
    rain_today = float(daily.get("precipitation_sum", [0])[0] or 0)

    # ── Derived farming signals ────────────────────────────────
    rain_risk = "high" if rain_today >= 10 else ("moderate" if rain_today >= 3 else "low")
    heat_stress = (
        "severe" if temp >= 38 else "high" if temp >= 34 else
        "moderate" if temp >= 30 else "low"
    )
    # Volumetric soil moisture → qualitative label (approximate bands)
    soil_state = (
        "waterlogged" if soil_moisture >= 0.42 else
        "moist" if soil_moisture >= 0.28 else
        "slightly dry" if soil_moisture >= 0.18 else "dry"
    )
    disease_pressure = (
        "high" if humidity >= 80 and temp >= 24 else
        "moderate" if humidity >= 65 else "low"
    )

    return {
        "location": {
            "name": location.get("name", place),
            "admin1": location.get("admin1", ""),
            "country": location.get("country", ""),
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "elevation": location.get("elevation"),
        },
        "current": {
            "temperature_c": round(temp, 1),
            "humidity_pct": round(humidity, 1),
            "precipitation_mm": round(float(current.get("precipitation") or 0), 1),
            "wind_kph": round(float(current.get("wind_speed_10m") or 0), 1),
            "soil_temperature_c": round(float(current.get("soil_temperature_0cm") or 0), 1),
            "soil_moisture_pct": round(soil_moisture * 100, 1),
            "weather_code": current.get("weather_code"),
        },
        "daily": {
            "temp_max_7d": [round(v, 1) for v in daily.get("temperature_2m_max", [])],
            "temp_min_7d": [round(v, 1) for v in daily.get("temperature_2m_min", [])],
            "rain_sum_7d": [round(v, 1) for v in daily.get("precipitation_sum", [])],
            "rain_probability_7d": daily.get("precipitation_probability_max", []),
            "et0_evapotranspiration_7d": [
                round(v, 2) for v in daily.get("et0_fao_evapotranspiration", [])
            ],
            "dates": daily.get("time", []),
        },
        "signals": {
            "rain_risk": rain_risk,
            "heat_stress": heat_stress,
            "soil_state": soil_state,
            "disease_pressure": disease_pressure,
            "total_rain_7d_mm": round(sum(daily.get("precipitation_sum", []) or []), 1),
        },
        "timezone": data.get("timezone", "auto"),
    }