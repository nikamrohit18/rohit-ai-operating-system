from agents.base import BaseAgent
from orchestrator.state import OrchestratorState
from tools.search import search_web, format_search_results
from tools.pdf import extract_pdf_text

SYSTEM_PROMPT = """You are a deep research analyst working for Rohit Nikam.
Synthesize the provided sources into comprehensive, well-structured research.
Include: key facts, current trends, expert perspectives, and actionable insights.
Cite sources by their URL when referencing specific claims.
Format your response with clear sections and bullet points where appropriate.
If no external sources are provided, draw on your training knowledge and note the limitation."""


class ResearchAgent(BaseAgent):
    name = "research"

    def run(self, state: OrchestratorState) -> dict:
        try:
            context = state.get("context") or {}

            # Web search
            search_results = search_web(state["input"])
            search_context = format_search_results(search_results)
            sources = [r.get("url") for r in search_results if r.get("url")]

            # PDF sources (accepts list or single string)
            pdf_context = ""
            pdf_sources = context.get("pdf_urls") or context.get("pdf_paths") or []
            if isinstance(pdf_sources, str):
                pdf_sources = [pdf_sources]
            for src in pdf_sources:
                try:
                    text = extract_pdf_text(src)
                    pdf_context += f"\n\n## PDF: {src}\n{text}"
                    sources.append(src)
                except Exception as e:
                    pdf_context += f"\n\n## PDF: {src}\n[Error reading PDF: {e}]"

            user_prompt = f"Research query: {state['input']}"
            if search_context:
                user_prompt += f"\n\n{search_context}"
            if pdf_context:
                user_prompt += pdf_context
            if not search_context and not pdf_context:
                user_prompt += "\n\n(No external sources available — draw on your training knowledge.)"

            output = self.call_claude(
                system=SYSTEM_PROMPT,
                user=user_prompt,
                max_tokens=4096,
            )
            return {"output": output, "status": "completed", "sources": sources}
        except Exception as e:
            return {"output": None, "status": "failed", "error": str(e)}


_agent = ResearchAgent()


def run(state: OrchestratorState) -> dict:
    return _agent.run(state)
