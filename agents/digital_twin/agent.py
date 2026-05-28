from agents.base import BaseAgent
from orchestrator.state import OrchestratorState
from memory.vector_store import VectorStore

SYSTEM_PROMPT = """You are the AI digital twin of Rohit Nikam — a tech professional, AI systems architect, content creator, and entrepreneur.

You have access to a curated knowledge base about Rohit. Use the provided context to answer accurately.
Speak in first person as Rohit's representative: warm, knowledgeable, and direct.
If the context doesn't cover a question, say so honestly — never fabricate details about Rohit.

Rohit's communication style:
- Professional but approachable
- Tech-forward, loves talking about AI and systems
- Grounded in real experience, not just theory
- Honest about what he knows and doesn't know"""


class DigitalTwinAgent(BaseAgent):
    name = "digital_twin"

    def __init__(self):
        super().__init__()
        self._vector_store: VectorStore | None = None

    @property
    def vector_store(self) -> VectorStore:
        if self._vector_store is None:
            self._vector_store = VectorStore()
        return self._vector_store

    def run(self, state: OrchestratorState) -> dict:
        try:
            results = self.vector_store.search(state["input"], limit=5)
            context_chunks = [r["text"] for r in results if r["score"] > 0.3]

            user_prompt = state["input"]
            if context_chunks:
                context_block = "\n\n".join(f"- {chunk}" for chunk in context_chunks)
                user_prompt = (
                    f"Relevant knowledge about Rohit:\n{context_block}"
                    f"\n\n---\nQuestion: {state['input']}"
                )

            output = self.call_claude(
                system=SYSTEM_PROMPT,
                user=user_prompt,
                max_tokens=2048,
            )
            return {"output": output, "status": "completed"}
        except Exception as e:
            return {"output": None, "status": "failed", "error": str(e)}


_agent = DigitalTwinAgent()


def run(state: OrchestratorState) -> dict:
    return _agent.run(state)
