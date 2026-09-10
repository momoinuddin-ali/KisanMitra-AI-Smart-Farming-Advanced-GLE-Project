# 🌾 KisanMitra AI — The Smart Farming Advice Agent

**IBM University Engagement Project Submission** · *Problem Statement No.14 — AI Agent for Smart Farming Advice*

> **Kisan** (farmer) + **Mitra** (friend) — an agentic AI companion that gives every farmer a free, personal agriculture expert.

---

## 💡 The Problem
Indian farmers lose up to **30–40% of potential income** to preventable causes — wrong irrigation timing, undetected pest outbreaks, poor fertilizer schedules, and distress selling at the wrong market moment. Expert agronomist advice exists, but one KVK scientist serves thousands of farmers. Advice does not scale. **KisanMitra AI does.**

## 🧠 The Solution — A 4-Agent Collaborative System

| # | Agent | What it does | Data source |
|---|-------|--------------|-------------|
| **1** | **Weather & Irrigation Agent** | Live weather + soil analysis → ET₀-based irrigation plan + 7-day field-work windows. | Open-Meteo API *(free, no key)* |
| **2** | **Crop Advisory Agent** | RAG over a bundled crop-knowledge base → personalized package of practice, fertilizer schedule, do's & don'ts. | `data/crop_knowledge.json` |
| **3** | **Pest/Disease Detection Agent** | **Multimodal**: farmer uploads a leaf photo → **Grok Vision** identifies the threat → organic + chemical remedies + prevention. | Photo + symptoms + live weather |
| **4** | **Market Insights Agent** | Mandi price-trend analysis → SELL / HOLD / SPLIT recommendation, expected price band, best channel, income tip. | `data/market_prices.json` |

*All agents share one context (live farm snapshot + farmer profile) and are powered by Grok models from xAI — `grok-3-mini` for reasoning, `grok-2-vision` for image analysis.*

---

## 🗂 Project Structure

```text
kisanmitra/
├── .env                    ← API keys (GROK_API_KEY) + settings
├── .env.example            ← template to copy
├── requirements.txt        ← flask, openai, python-dotenv, requests
├── main_core.py            ← multi-agent orchestration engine (CLI)
├── app.py                  ← Flask web server + REST API
├── index.html              ← farmer dashboard (single-page)
├── style.css               ← farm-warm dashboard styling
├── config.py               ← settings loader
├── agents/
│   ├── base_agent.py       ← Grok (xAI) LLM wrapper + retries + JSON mode
│   ├── weather_irrigation_agent.py
│   ├── crop_advisory_agent.py
│   ├── pest_detection_agent.py
│   └── market_insights_agent.py
├── data/
│   ├── crop_knowledge.json ← RAG knowledge base (11 crops)
│   └── market_prices.json  ← mandi price series (INR/quintal)
└── utils/
    └── weather_client.py   ← Open-Meteo free API client + cache
```
🚀 Quick Start
# 1. Install dependencies
pip install -r requirements.txt

# 2. Get your FREE Grok API key
#    → [https://console.x.ai](https://console.x.ai)  → API Keys → Create API Key
#    (xAI gives free credits to students)

# 3. Put the key in your .env file
#    GROK_API_KEY=xai-xxxxxxxxxxxxxxxx

# 4a. Run the web dashboard
python app.py                       
# → http://localhost:5000

# 4b. …or run the CLI pipeline
python main_core.py --place Nashik --crop wheat --stage flowering

# 4c. …with symptoms + a crop photo (Grok Vision):
python main_core.py --place Ludhiana --crop rice --stage tillering \
    --symptoms "yellow spots on lower leaves" \
    --image ./samples/leaf.jpg --json-out report.json
No API key yet? No problem — every agent has a rule-based fallback (ET₀ math, RAG retrieval, weather-driven disease pressure, price statistics) so the full pipeline still demos end-to-end without failing.
Method,Endpoint,Purpose
GET,/,Farmer dashboard UI
GET,/api/crops,Supported crops list
GET,/api/health,Status + checks which AI engine is live
POST,/api/analyze,"Runs full 4-agent pipeline {place, crop, stage, symptoms, acres, quintals}"
POST,/api/analyze-photo,Photo upload → Grok Vision pest analysis (multipart form)
🔑 Why Grok + Open-Meteo (All Free)?

    Grok (xAI): OpenAI-compatible endpoint (https://api.x.ai/v1), free signup credits, highly capable reasoning and vision models.

    Open-Meteo: Fetches live weather + soil moisture/temperature + ET₀ (FAO-56) for any coordinate on Earth. No API key required.

    Local RAG Knowledge Base: Runs entirely offline; the retrieval step (CropAdvisoryAgent.retrieve()) scores entries by crop + stage relevance before Grok generates advice.

✨ Novelty & Uniqueness

    ET₀-based irrigation math: Uses real FAO evapotranspiration data from live APIs, completely eliminating guesswork.

    Multimodal pest detection: Farmer's own photo → Grok Vision → instant organic + chemical remedies.

    Farm-to-market loop: The only farming agent that ends with actual income optimization advice (sell/hold + price band + channel).

    Weather-aware disease pressure: Humidity × temperature signals prime the pest agent before physical symptoms even appear.

    Graceful degradation: Every agent works with or without the Grok key. The system never crashes during a demo.

🔭 Future Scope

    Regional Language Support: Adding voice input for Hindi, Marathi, Telugu, and Punjabi.

    Satellite Telemetry: NDVI integration for plot-level crop health monitoring.

    Live Market APIs: e-NAM live price integration for real-time bidding trends.

    WhatsApp Bot Channel: Increasing accessibility for feature-phone users.

    IoT Actuation: Drip-irrigation smart pump control integration.

📄 Submission Note

Built for the IBM University Engagement Program — "Exploring the Power of Agentic AI". The agent roles map exactly to the multi-agent system specified in Problem Statement No.14, and the pipeline is designed to be easily portable to IBM watsonx.ai / Granite endpoints by changing a single base URL in the .env file.
