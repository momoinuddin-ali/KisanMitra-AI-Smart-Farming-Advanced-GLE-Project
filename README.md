🌾 KisanMitra AI — The Smart Farming Advice Agent

IBM University Engagement Project Submission · Problem Statement No.14 — AI Agent for Smart Farming Advice

    Kisan (farmer) + Mitra (friend) — an agentic AI companion that gives every farmer a free, personal agriculture expert.

💡 The Problem

Indian farmers lose up to 30–40% of potential income to preventable causes — wrong irrigation timing, undetected pest outbreaks, poor fertilizer schedules, and distress selling at the wrong market moment. Expert agronomist advice exists, but one KVK scientist serves thousands of farmers. Advice does not scale. KisanMitra AI does.
🧠 The Solution — a 4-Agent Collaborative System
#	Agent	What it does	Data source
1	Weather & Irrigation Agent	Live weather + soil analysis → ET₀-based irrigation plan + 7-day field-work windows	Open-Meteo API (free, no key)
2	Crop Advisory Agent	RAG over a bundled crop-knowledge base → personalized package of practice, fertilizer schedule, do's & don'ts	data/crop_knowledge.json (ICAR-style distilled guidelines)
3	Pest/Disease Detection Agent	Multimodal: farmer uploads a leaf photo → Grok Vision identifies the threat → organic + chemical remedies + prevention	Photo + symptoms + live weather
4	Market Insights Agent	Mandi price-trend analysis → SELL / HOLD / SPLIT recommendation, expected price band, best channel, income tip	data/market_prices.json (mandi sample series)

All agents share one context (live farm snapshot + farmer profile) and are powered by Grok models from xAI — grok-3-mini for reasoning, grok-2-vision for image analysis.
🗂 Project Structure

kisanmitra/├── .env                    ← API keys (GROK_API_KEY) + settings├── .env.example            ← template to copy├── requirements.txt        ← flask, openai, python-dotenv, requests├── main_core.py            ← multi-agent orchestration engine (CLI)├── app.py                  ← Flask web server + REST API├── index.html              ← farmer dashboard (single-page)├── style.css               ← farm-warm dashboard styling├── config.py               ← settings loader├── agents/│   ├── base_agent.py       ← Grok (xAI) LLM wrapper + retries + JSON mode│   ├── weather_irrigation_agent.py│   ├── crop_advisory_agent.py│   ├── pest_detection_agent.py│   └── market_insights_agent.py├── data/│   ├── crop_knowledge.json ← RAG knowledge base (11 crops)│   └── market_prices.json  ← mandi price series (INR/quintal)└── utils/    └── weather_client.py   ← Open-Meteo free API client + cache

🚀 Quick Start

# 1. Install dependenciespip install -r requirements.txt# 2. Get your FREE Grok API key#    → https://console.x.ai  → API Keys → Create API Key#    (xAI gives free credits to students)# 3. Put the key in .env#    GROK_API_KEY=xai-xxxxxxxxxxxxxxxx# 4a. Run the web dashboardpython app.py                       # → http://localhost:5000# 4b. …or run the CLI pipelinepython main_core.py --place Nashik --crop wheat --stage flowering#    with symptoms + a crop photo (Grok Vision):python main_core.py --place Ludhiana --crop rice --stage tillering \    --symptoms "yellow spots on lower leaves" \    --image ./samples/leaf.jpg --json-out report.json

    No API key yet? No problem — every agent has a rule-based fallback (ET₀ math, RAG retrieval, weather-driven disease pressure, price statistics) so the full pipeline still demos end-to-end.

🔌 API Endpoints (app.py)
Method	Endpoint	Purpose
GET	/	Farmer dashboard
GET	/api/crops	Supported crops list
GET	/api/health	Status + which engine is live
POST	/api/analyze	Full 4-agent pipeline {place, crop, stage, symptoms, acres, quintals}
POST	/api/analyze-photo	Photo upload → Grok Vision pest analysis (multipart form)
🔑 Why Grok + Open-Meteo (all free)?

    Grok (xAI) — OpenAI-compatible endpoint (https://api.x.ai/v1), free signup credits, strong reasoning and vision models.
    Open-Meteo — weather + soil moisture/temperature + ET₀ (FAO-56) for any coordinate on Earth. No API key, no limit worries.
    Local RAG knowledge base — runs offline; the retrieval step (CropAdvisoryAgent.retrieve()) scores entries by crop + stage relevance before Grok generates advice.

✨ Novelty

    ET₀-based irrigation math — real FAO evapotranspiration from live API, not guesswork.
    Multimodal pest detection — farmer's own photo → Grok Vision → organic + chemical remedy.
    Farm-to-market loop — the only farming agent that ends with income advice (sell/hold + price band + channel).
    Weather-aware disease pressure — humidity × temperature signals prime the pest agent before symptoms appear.
    Graceful degradation — every agent works with or without the Grok key. The demo never fails.

🔭 Future Scope

    Regional language support (Hindi, Marathi, Telugu, Punjabi) with voice input
    Satellite NDVI integration for plot-level crop health
    e-NAM live price API integration
    WhatsApp bot channel for feature-phone farmers
    Drip-irrigation pump control integration (IoT actuation)

📄 Submission Note

Built for the IBM University Engagement Program — "Exploring the Power of Agentic AI". The agent roles map exactly to the multi-agent system specified in Problem Statement No.14, and the pipeline is designed to be portable to IBM watsonx.ai / Granite endpoints by changing one base URL in .env.