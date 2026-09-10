import config
class BaseAgent:
    NAME = "BaseAgent"
    ROLE = "base"
    def __init__(self):
        self.client = None
        self.token_usage = 0
    def status(self) -> str:
        return "fallback"
