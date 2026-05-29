from abc import ABC, abstractmethod
import anthropic
from config import get_settings
from orchestrator.state import OrchestratorState

SONNET = "claude-sonnet-4-6"
HAIKU = "claude-haiku-4-5-20251001"


class BaseAgent(ABC):
    name: str = "base"

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=get_settings().anthropic_api_key)

    def call_claude(self, system: str, user: str, model: str = SONNET, max_tokens: int = 2048) -> str:
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text

    def call_claude_fast(self, system: str, user: str) -> str:
        return self.call_claude(system, user, model=HAIKU, max_tokens=1024)

    def call_claude_with_history(
        self, system: str, messages: list, model: str = SONNET, max_tokens: int = 2048
    ) -> str:
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return response.content[0].text

    @abstractmethod
    def run(self, state: OrchestratorState) -> dict:
        pass
