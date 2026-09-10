"""
agents/market_insights_agent.py — Market Insights Agent (Agent 4).

Job:
  • Reads the bundled mandi (market) price dataset
    (data/market_prices.json — realistic sample series per crop)
  • Grok analyzes the price trend, volatility and seasonal pattern
  • Returns: sell-now vs hold recommendation, expected price band,
    best market channel, and one income optimization tip.

This is the "farm-to-market intelligence" piece that turns agronomy
into actual income advice — the differentiator of KisanMitra.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any, Dict, List

from agents.base_agent import BaseAgent

PRICE_PATH = Path(__file__).resolve().parent.parent / "data" / "market_prices.json"

SYSTEM_PROMPT = (
    "You are the Market Insights Agent of KisanMitra. You receive recent "
    "mandi (APMC market) price series for the farmer's crop plus quantity "
    "and farm details. Analyze trend and volatility, then advise: sell or "
    "hold, expected price band, best channel, and one concrete income tip. "
    "Prices are INR per quintal (1 quintal = 100 kg). Simple English."
)


class MarketInsightsAgent(BaseAgent):
    NAME = "Market Insights Agent"
    ROLE = "market_insights"

    def __init__(self) -> None:
        super().__init__()
        self.prices = self._load_prices()

    @staticmethod
    def _load_prices() -> Dict[str, List[float]]:
        try:
            with open(PRICE_PATH, encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, json.JSONDecodeError):
            return {}

    def _price_series(self, crop: str) -> List[float]:
        """Return the price series for a crop (falls back to the closest key)."""
        crop_l = crop.lower()
        for key in self.prices:
            if key.lower() == crop_l or crop_l in key.lower():
                return self.prices[key]
        return next(iter(self.prices.values()), []) if self.prices else []

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        crop_profile = context.get("crop_profile", {})
        crop = crop_profile.get("crop", "wheat")
        series = self._price_series(crop)

        grok_result = self.ask_grok_json(
            SYSTEM_PROMPT, self._build_prompt(crop, crop_profile, series)
        )
        if grok_result and "recommendation" in grok_result:
            grok_result["source"] = "grok"
            grok_result["tokens_used"] = self.token_usage
            return grok_result
        return self._fallback(crop, series)

    @staticmethod
    def _build_prompt(crop: str, profile: Dict, series: List[float]) -> str:
        return (
            f"Crop: {crop} | Farm size: {profile.get('size_acres', 2)} acres | "
            f"Expected produce: {profile.get('expected_quintals', 40)} quintals\n"
            f"Recent mandi prices (INR/quintal, oldest→newest): {series}\n"
            "Return JSON keys: recommendation (SELL NOW / HOLD / SPLIT), "
            "reason (1-2 sentences), expected_price_band (object with low and "
            "high, INR/quintal), best_channel (string), income_tip (string)."
        )

    @staticmethod
    def _fallback(crop: str, series: List[float]) -> Dict[str, Any]:
        if len(series) < 3:
            return {
                "agent": "Market Insights Agent",
                "recommendation": "HOLD",
                "reason": "Insufficient price history — monitor mandi rates this week.",
                "expected_price_band": {"low": 0, "high": 0},
                "best_channel": "Local APMC mandi",
                "income_tip": "Register on e-NAM for live price discovery.",
                "source": "rule-based fallback",
                "tokens_used": 0,
            }

        latest = series[-1]
        mean_price = statistics.mean(series)
        trend = latest - mean_price
        pct = (trend / mean_price) * 100 if mean_price else 0

        if pct > 4:
            rec, reason = "SELL NOW", (
                f"Current price ₹{latest:.0f}/qtl is {pct:.1f}% above the recent "
                f"average ₹{mean_price:.0f} — good exit window."
            )
        elif pct < -4:
            rec, reason = "HOLD", (
                f"Price ₹{latest:.0f}/qtl is {abs(pct):.1f}% below average "
                f"₹{mean_price:.0f} — wait for recovery if storage allows."
            )
        else:
            rec, reason = "SPLIT", (
                f"Price ₹{latest:.0f}/qtl is stable near average ₹{mean_price:.0f} — "
                "sell in two lots to average out."
            )

        return {
            "agent": "Market Insights Agent",
            "recommendation": rec,
            "reason": reason,
            "expected_price_band": {
                "low": round(min(series[-6:]) if series else 0),
                "high": round(max(series[-6:]) if series else 0),
            },
            "best_channel": "e-NAM registered local APMC for best transparency",
            "income_tip": "Grade and clean produce before selling — grade-1 lots "
                          "typically fetch 4-8% more at mandi.",
            "source": "rule-based fallback",
            "tokens_used": 0,
        }