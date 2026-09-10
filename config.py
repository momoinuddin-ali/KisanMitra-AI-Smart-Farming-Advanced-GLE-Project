"""
config.py — Central settings loader for KisanMitra AI.

Loads all configuration from the .env file (Grok API key, model names,
Open-Meteo endpoints, app settings) and exposes them as typed constants.

Rule of thumb: never hard-code secrets in code — everything lives in .env.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load the .env file that sits next to this script
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _get_int(name: str, default: int) -> int:
    """Read an integer setting from the environment with a safe fallback."""
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


# ── Grok API (xAI) settings ────────────────────────────────────
GROK_API_KEY = os.getenv("GROK_API_KEY", "").strip()
GROK_MODEL = os.getenv("GROK_MODEL", "grok-3-mini").strip()
GROK_VISION_MODEL = os.getenv("GROK_VISION_MODEL", "grok-2-vision-1212").strip()
GROK_BASE_URL = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1").strip()

# True when the student has replaced the placeholder with a real key
GROK_ENABLED = bool(GROK_API_KEY) and not GROK_API_KEY.startswith("xai-your")

# ── Open-Meteo (free, keyless) endpoints ───────────────────────
GEOCODING_URL = os.getenv(
    "OPEN_METEO_GEOCODING_URL", "https://geocoding-api.open-meteo.com/v1/search"
)
FORECAST_URL = os.getenv(
    "OPEN_METEO_FORECAST_URL", "https://api.open-meteo.com/v1/forecast"
)

# ── Application settings ───────────────────────────────────────
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = _get_int("FLASK_PORT", 5000)
CACHE_TTL_MINUTES = _get_int("CACHE_TTL_MINUTES", 30)
REQUEST_TIMEOUT = _get_int("REQUEST_TIMEOUT_SECONDS", 15)
FORECAST_DAYS = _get_int("FORECAST_DAYS", 7)