from agents.base import BaseAgent
from orchestrator.state import OrchestratorState
from tools.search import search_web, format_search_results

SYSTEM_PROMPT = """You are Rohit Nikam's YouTube content strategist and scriptwriter.
Rohit creates content about AI agents, LLM engineering, automation, and building real systems.
Based in Bangkok. Builds and ships — no theory without code.

Content guidelines:
- Titles: 50-60 chars, strongest keyword first, curiosity or benefit hook, no clickbait
- Description: First 2-3 lines are critical (shown before "Show more"), then timestamps, links, hashtags
- Script outline: Hook (0:00-0:30) → Problem/Opportunity → Solution walkthrough → Key takeaways → CTA
- Tags: Mix broad (AI, LLM, automation) and specific (LangGraph tutorial, Claude API, AI agents Python)
- Thumbnail text: 3-5 bold words max — what makes someone stop scrolling

Rohit's YouTube persona: the builder who actually ships — not slides, not theory, working systems."""

CONTENT_TYPE_INSTRUCTIONS = {
    "script_only": (
        "Write a complete YouTube video script with timestamps. "
        "Include: Hook (0:00-0:30), main content sections with speaker notes, and outro with CTA. "
        "Format as a real shooting script."
    ),
    "metadata_only": (
        "Generate YouTube metadata only:\n"
        "## TITLES (3 options, best to weakest)\n"
        "## DESCRIPTION (full, with [TIMESTAMP] placeholders and 3-5 hashtags at end)\n"
        "## TAGS (15-20 comma-separated tags)"
    ),
    "full_package": (
        "Generate a complete YouTube content package with these clearly labeled sections:\n"
        "## TITLES (3 options, ranked best to weakest)\n"
        "## DESCRIPTION (full description with [TIMESTAMP] placeholders, links section, hashtags)\n"
        "## SCRIPT OUTLINE (section-by-section with talking points and estimated timing)\n"
        "## TAGS (15-20 tags)\n"
        "## THUMBNAIL CONCEPT (3-5 word text overlay + visual concept description)"
    ),
}


class YouTubeAgent(BaseAgent):
    name = "youtube"

    def run(self, state: OrchestratorState) -> dict:
        try:
            context = state.get("context") or {}
            content_type = context.get("content_type", "full_package")
            research_results = context.get("research_results", "")

            search_context = ""
            if context.get("search_web"):
                results = search_web(state["input"], max_results=5)
                search_context = format_search_results(results)

            instructions = CONTENT_TYPE_INSTRUCTIONS.get(
                content_type, CONTENT_TYPE_INSTRUCTIONS["full_package"]
            )
            user_prompt = f"Video topic: {state['input']}\n\n{instructions}"
            if research_results:
                user_prompt += f"\n\n## Research Context\n{research_results}"
            if search_context:
                user_prompt += f"\n\n## Trending/SERP Context\n{search_context}"

            output = self.call_claude(
                system=SYSTEM_PROMPT,
                user=user_prompt,
                max_tokens=6000,
            )
            return {"output": output, "status": "completed"}
        except Exception as e:
            return {"output": None, "status": "failed", "error": str(e)}


_agent = YouTubeAgent()


def run(state: OrchestratorState) -> dict:
    return _agent.run(state)
