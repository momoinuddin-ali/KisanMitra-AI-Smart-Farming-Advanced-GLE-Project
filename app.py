"""
app.py — Flask web server for KisanMitra AI.

Serves the farmer dashboard (index.html + style.css) and exposes:

    GET  /                  → the dashboard
    GET  /api/crops         → list of supported crops
    POST /api/analyze       → run the full 4-agent pipeline
                              accepts BOTH:
                                • JSON  {place, crop, stage, symptoms, acres, quintals}
                                • multipart form-data with an optional "photo"
                                  field → feeds the Pest Detection Agent (vision)
    POST /api/analyze-photo → photo upload only → Pest Detection Agent (kept
                              for API compatibility / direct testing)

Run:
    python app.py           → http://localhost:5000
"""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any, Dict, Optional

from flask import Flask, jsonify, request, send_from_directory

import config
from main_core import build_context, run_pipeline

app = Flask(__name__, static_folder=".", static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB photo limit


# ── Static routes (the dashboard) ─────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/<path:path>")
def assets(path: str):
    """Serve style.css and any static asset next to app.py."""
    return send_from_directory(".", path)


@app.route("/api/crops")
def crops():
    """List of crops the knowledge base supports (drives the UI dropdown)."""
    try:
        with open(os.path.join("data", "crop_knowledge.json"), encoding="utf-8") as fh:
            kb = json.load(fh)
        supported = sorted({entry["crop"] for entry in kb})
    except (OSError, json.JSONDecodeError):
        supported = ["wheat", "rice", "cotton", "tomato"]
    return jsonify({"crops": supported})


# ── Helpers ───────────────────────────────────────────────────

def _save_upload(photo) -> Optional[str]:
    """Persist an uploaded photo to a temp file; return its path or None."""
    if not photo or not photo.filename:
        return None
    suffix = os.path.splitext(photo.filename)[1].lower() or ".jpg"
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    photo.save(tmp.name)
    tmp.close()
    return tmp.name


def _analyze(place: str, crop: str, stage: str, symptoms: str,
             acres: float, quintals: float,
             image_path: Optional[str] = None) -> tuple:
    """Shared pipeline runner used by /api/analyze and /api/analyze-photo."""
    context = build_context(
        place=place, crop=crop, stage=stage, symptoms=symptoms,
        size_acres=acres, expected_quintals=quintals,
        image_path=image_path,
    )
    if not context:
        return (jsonify({
            "error": f"Could not find '{place}'. Check the spelling or try a nearby town."
        }), 404)
    report = run_pipeline(context)
    return (jsonify(report), 200)


# ── Core agent endpoints ──────────────────────────────────────

@app.route("/api/analyze", methods=["POST"])
def analyze():
    """Run the full multi-agent pipeline for a farmer query.

    Accepts JSON OR multipart/form-data (with an optional 'photo' file).
    The photo flows straight into the Pest Detection Agent inside the
    SAME pipeline — no separate call needed.
    """
    content_type = (request.content_type or "").lower()

    image_path: Optional[str] = None
    cleanup: Optional[str] = None

    try:
        if content_type.startswith("multipart/form-data"):
            f = request.form
            place = str(f.get("place", "")).strip()
            crop = str(f.get("crop", "wheat")).strip().lower()
            stage = str(f.get("stage", "vegetative")).strip().lower()
            symptoms = str(f.get("symptoms", "")).strip()
            acres = float(f.get("acres", 2.0) or 2.0)
            quintals = float(f.get("quintals", 40.0) or 40.0)
            image_path = _save_upload(request.files.get("photo"))
            cleanup = image_path
        else:
            payload: Dict[str, Any] = request.get_json(silent=True) or {}
            place = str(payload.get("place", "")).strip()
            crop = str(payload.get("crop", "wheat")).strip().lower()
            stage = str(payload.get("stage", "vegetative")).strip().lower()
            symptoms = str(payload.get("symptoms", "")).strip()
            acres = float(payload.get("acres", 2.0) or 2.0)
            quintals = float(payload.get("quintals", 40.0) or 40.0)

        if not place:
            return jsonify({"error": "place is required"}), 400

        return _analyze(place, crop, stage, symptoms, acres, quintals, image_path)
    finally:
        if cleanup:
            try:
                os.unlink(cleanup)
            except OSError:
                pass


@app.route("/api/analyze-photo", methods=["POST"])
def analyze_photo():
    """Crop photo → Pest/Disease Detection Agent (standalone vision test)."""
    if "photo" not in request.files:
        return jsonify({"error": "photo file is required"}), 400

    place = str(request.form.get("place", "")).strip() or "Nashik"
    crop = str(request.form.get("crop", "wheat")).strip().lower()
    stage = str(request.form.get("stage", "vegetative")).strip().lower()
    symptoms = str(request.form.get("symptoms", "")).strip()

    tmp_path = _save_upload(request.files.get("photo"))
    if not tmp_path:
        return jsonify({"error": "photo file is required"}), 400

    try:
        context = build_context(place=place, crop=crop, stage=stage,
                                 symptoms=symptoms, image_path=tmp_path)
        if not context:
            return jsonify({"error": f"Could not resolve location '{place}'."}), 404

        from agents import PestDetectionAgent
        agent = PestDetectionAgent()
        result = agent.run(context)
        result["engine"] = agent.status()
        return jsonify(result)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "llm_enabled": config.GROK_ENABLED,
        "provider": "custom API" if config.GROK_ENABLED else "fallback-mode",
        "text_model": config.GROK_MODEL if config.GROK_ENABLED else "fallback",
        "vision_model": config.GROK_VISION_MODEL if config.GROK_ENABLED else "fallback",
    })


# ── Entry point ───────────────────────────────────────────────

if __name__ == "__main__":
    mode = "LLM live" if config.GROK_ENABLED else "fallback (set your API key in .env!)"
    print(f"[KisanMitra] dashboard → http://localhost:{config.FLASK_PORT}")
    print(f"   text model : {config.GROK_MODEL}")
    print(f"   vision model: {config.GROK_VISION_MODEL}")
    print(f"   engine     : {mode}\n")
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=False)