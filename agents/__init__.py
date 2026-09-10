"""
agents/__init__.py — Multi-agent lineup for KisanMitra AI.

The four agents defined in Problem Statement No.14:
  1. WeatherIrrigationAgent  — weather + soil + ET0 → irrigation plan
  2. CropAdvisoryAgent       — RAG knowledge → package of practice
  3. PestDetectionAgent      — Grok Vision + symptoms → threat + remedy
  4. MarketInsightsAgent     — mandi price trends → sell/hold advice
"""

from agents.base_agent import BaseAgent
from agents.crop_advisory_agent import CropAdvisoryAgent
from agents.market_insights_agent import MarketInsightsAgent
from agents.pest_detection_agent import PestDetectionAgent
from agents.weather_irrigation_agent import WeatherIrrigationAgent

__all__ = [
    "BaseAgent",
    "WeatherIrrigationAgent",
    "CropAdvisoryAgent",
    "PestDetectionAgent",
    "MarketInsightsAgent",
]

AGENT_REGISTRY = {
    "weather_irrigation": WeatherIrrigationAgent,
    "crop_advisory": CropAdvisoryAgent,
    "pest_detection": PestDetectionAgent,
    "market_insights": MarketInsightsAgent,
}