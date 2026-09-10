from agents.base_agent import BaseAgent
class CropAdvisoryAgent(BaseAgent):
    NAME = "Crop Advisory Agent"
    ROLE = "crop_advisory"
    def run(self, context):
        return {
            "agent": self.NAME, "source": "rule-based fallback", "tokens_used": 0,
            "package_of_practice": "Standard package of practice based on retrieved knowledge.",
            "fertilizer_plan": [{"input": "Balanced NPK", "dose": "Soil-test based", "timing": "Current stage"}],
            "dos": ["Test soil health", "Use certified seeds"],
            "donts": ["Avoid over-irrigation", "Do not spray blindly"]
        }
