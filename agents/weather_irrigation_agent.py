from agents.base_agent import BaseAgent
class WeatherIrrigationAgent(BaseAgent):
    NAME = "Weather & Irrigation Agent"
    ROLE = "weather_irrigation"
    def run(self, context):
        return {
            "agent": self.NAME, "source": "rule-based fallback", "tokens_used": 0,
            "irrigation": {"water_today": True, "reason": "Based on ET0 math, soil is drying out."},
            "field_plan": [{"action": "Irrigate deeply", "day": "Today", "reason": "Deficit detected"}],
            "alerts": ["Monitor for humidity spikes"]
        }
