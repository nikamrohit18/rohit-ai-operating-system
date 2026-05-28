from agents.base import BaseAgent
from orchestrator.state import OrchestratorState
from tools.search import search_web, format_search_results

SYSTEM_PROMPT = """You are Rohit Nikam's personal content strategist and ghostwriter.
Write in Rohit's voice: professional yet approachable, insightful, tech-forward, grounded in real experience.

For LinkedIn posts:
- Open with a strong hook (no "I am excited to share" openers)
- Keep it concise and value-packed
- End with a clear CTA or thought-provoking question
- Use line breaks for readability, avoid walls of text

For blogs/articles:
- Clear structure with H2/H3 headings
- SEO-aware without being keyword-stuffed
- Practical takeaways the reader can act on immediately

Always ask: "Would Rohit actually say this?" If not, rewrite."""


class ContentAgent(BaseAgent):
    name = "content"

    def run(self, state: OrchestratorState) -> dict:
        try:
            context = state.get("context") or {}
            content_type = context.get("content_type", "linkedin_post")
            research_results = context.get("research_results", "")

            # Optional web search for current context (caller sets context.search_web = true)
            search_context = ""
            if context.get("search_web"):
                results = search_web(state["input"], max_results=3)
                search_context = format_search_results(results)

            user_prompt = f"Content type: {content_type}\n\nTopic/Brief:\n{state['input']}"
            if research_results:
                user_prompt += f"\n\n## Research Context\n{research_results}"
            if search_context:
                user_prompt += f"\n\n{search_context}"

            output = self.call_claude(
                system=SYSTEM_PROMPT,
                user=user_prompt,
                max_tokens=4096,
            )
            return {"output": output, "status": "completed"}
        except Exception as e:
            return {"output": None, "status": "failed", "error": str(e)}


_agent = ContentAgent()


def run(state: OrchestratorState) -> dict:
    return _agent.run(state)
