from agents.base_agent import BaseAgent
class PestDetectionAgent(BaseAgent):
    NAME = "Pest/Disease Detection Agent"
    ROLE = "pest_detection"
    def run(self, context):
        return {
            "agent": self.NAME, "source": "rule-based fallback", "tokens_used": 0,
            "threat": "Low Risk / Monitor", "what_you_see": "No severe symptoms detected from inputs.",
            "organic_remedy": "Neem oil spray (3ml/L) as preventive", "chemical_remedy": "Not needed currently",
            "prevention": ["Maintain row spacing", "Scout field every 2 days"],
            "photo_received": False, "photo_analyzed": False, "vision_note": ""
        }
