"""
main_core.py — KisanMitra AI multi-agent orchestration engine.

This is the "conductor" of the agent pipeline (Problem Statement No.14):

    ┌────────────────────────────────────────────────────────┐
    │                     FARMER INPUT                        │
    │   location · crop · growth stage · symptoms · photo     │
    └────────────────────────┬───────────────────────────────┘
                             ▼
              ┌─────────────────────────────┐
              │  utils/weather_client.py    │  ← Open-Meteo (free, no key)
              └──────────────┬──────────────┘
                             ▼  farm snapshot (weather + soil + signals)
      ╔══════════════════════════════════════════════════╗
      ║  AGENT 1  Weather & Irrigation  → irrigation plan ║
      ║  AGENT 2  Crop Advisory (RAG)   → practice pack   ║
      ║  AGENT 3  Pest Detection        → threat + remedy ║
      ║  AGENT 4  Market Insights       → sell / hold     ║
      ╚══════════════════════════════════════════════════╝
                             ▼
                  final advisory report (JSON)
                consumed by app.py → index.html

Usage (CLI):
    python main_core.py --place Nashik --crop wheat --stage flowering
    python main_core.py --place Ludhiana --crop rice --symptoms "yellow spots on leaves"
"""

from __future__ import annotations

import argparse
import json
import time
from typing import Any, Dict

from agents import AGENT_REGISTRY
from utils import weather_client


def build_context(place: str, crop: str, stage: str, symptoms: str = "",
                  image_path: str | None = None, size_acres: float = 2.0,
                  expected_quintals: float = 40.0) -> Dict[str, Any] | None:
    """Gather live data + farmer profile into the shared agent context."""
    snapshot = weather_client.get_farm_snapshot(place)
    if not snapshot:
        return None

    return {
        "weather": snapshot,
        "crop_profile": {
            "crop": crop,
            "stage": stage,
            "size_acres": size_acres,
            "expected_quintals": expected_quintals,
        },
        "symptoms": symptoms,
        "image_path": image_path,
    }


def run_pipeline(context: Dict[str, Any]) -> Dict[str, Any]:
    """Run all 4 agents sequentially over the shared context."""
    report: Dict[str, Any] = {
        "location": context["weather"]["location"],
        "weather": context["weather"]["current"],
        "signals": context["weather"]["signals"],
        "daily": context["weather"]["daily"],
        "crop_profile": context["crop_profile"],
        "agents": {},
        "pipeline_started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    total_tokens = 0
    for role, agent_cls in AGENT_REGISTRY.items():
        agent = agent_cls()
        started = time.time()
        print(f"  ▶ running {agent.NAME} ...")
        try:
            result = agent.run(context)
        except Exception as exc:  # noqa: BLE001 — one agent must never kill the rest
            print(f"    ! {agent.NAME} error: {exc}")
            result = {"error": str(exc), "source": "error"}
        elapsed = round(time.time() - started, 2)
        tokens = result.get("tokens_used", 0)
        total_tokens += tokens
        result.setdefault("agent", agent.NAME)
        result["engine"] = agent.status()
        result["latency_seconds"] = elapsed
        report["agents"][role] = result
        print(f"    ✔ done in {elapsed}s via {result.get('source', agent.status())}")

    report["total_tokens_used"] = total_tokens
    report["pipeline_finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="KisanMitra AI — Smart Farming multi-agent advisor"
    )
    parser.add_argument("--place", required=True, help="village / city name")
    parser.add_argument("--crop", default="wheat", help="crop name (wheat, rice, cotton ...)")
    parser.add_argument("--stage", default="vegetative",
                        help="growth stage (seedling/tillering/flowering/fruiting ...)")
    parser.add_argument("--symptoms", default="", help="observed pest/disease symptoms")
    parser.add_argument("--image", dest="image_path", default=None,
                        help="path to crop photo for Grok Vision analysis")
    parser.add_argument("--acres", type=float, default=2.0, help="farm size in acres")
    parser.add_argument("--quintals", type=float, default=40.0,
                        help="expected harvest in quintals")
    parser.add_argument("--json-out", default=None, help="save the full report as JSON")
    args = parser.parse_args()

    print(f"\n🌾 KisanMitra AI — advisory for {args.place} ({args.crop}, {args.stage})\n")

    context = build_context(
        place=args.place, crop=args.crop, stage=args.stage,
        symptoms=args.symptoms, image_path=args.image_path,
        size_acres=args.acres, expected_quintals=args.quintals,
    )
    if not context:
        print("✖ Could not resolve that location or fetch live weather. Try another spelling.")
        return

    report = run_pipeline(context)

    # Pretty console summary
    w = report["weather"]
    print(f"\n📍 {report['location']['name']}, {report['location']['admin1']}")
    print(f"🌡  {w['temperature_c']}°C | 💧 {w['humidity_pct']}% humidity | "
          f"🌱 soil {w['soil_moisture_pct']}% | ☔ signals: {report['signals']}")
    for role, res in report["agents"].items():
        print(f"  • {res.get('agent', role)} [{res.get('source', '?')}]")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, default=str)
        print(f"\n💾 full report saved → {args.json_out}")
    print(f"\n🤖 total Grok tokens used: {report['total_tokens_used']}\n")


if __name__ == "__main__":
    main()