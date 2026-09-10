from agents.base_agent import BaseAgent
class MarketInsightsAgent(BaseAgent):
    NAME = "Market Insights Agent"
    ROLE = "market_insights"
    def run(self, context):
        return {
            "agent": self.NAME, "source": "rule-based fallback", "tokens_used": 0,
            "recommendation": "HOLD", "reason": "Prices are currently stable near the moving average.",
            "expected_price_band": {"low": 2100, "high": 2450},
            "best_channel": "Local APMC Mandi (e-NAM)", "income_tip": "Grade and clean produce before selling for a 5% premium."
        }
