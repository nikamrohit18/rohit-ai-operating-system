from agents.base import BaseAgent
from orchestrator.state import OrchestratorState
from tools.search import search_web, format_search_results

SYSTEM_PROMPT = """You are Rohit Nikam's social media strategist.
Write in Rohit's voice: direct, insightful, tech-forward, based in Bangkok building AI systems.

Rohit's content pillars: AI agents, LLM engineering, automation, building in public, Southeast Asia tech scene.

Platform guidelines:
- Twitter/X thread: Hook tweet → value tweets → CTA tweet. Each tweet ≤280 chars. Separate with '---'.
- Twitter/X post: Single punchy tweet ≤280 chars. No filler.
- Instagram: Strong hook line, readable paragraphs, 20-25 hashtags at end.
- LinkedIn: Professional hook, insight paragraphs, question or CTA at the end. No hollow buzzwords.
- All: Return all 4 formats with clear section headers.

Make every post feel written by a real person who ships things, not a content bot."""

PLATFORM_INSTRUCTIONS = {
    "twitter_thread": "Write a Twitter/X thread of 6-8 tweets. Tweet 1 = compelling hook. Tweets 2-6 = one insight per tweet. Last tweet = CTA or question. Separate tweets with '---'.",
    "twitter_post": "Write a single tweet. Max 280 characters. Sharp, no fluff.",
    "instagram_post": "Write an Instagram caption: hook line, 3-4 body paragraphs with line breaks, then 20-25 relevant hashtags separated by spaces.",
    "linkedin_post": "Write a LinkedIn post: bold opening hook, 3-4 paragraphs of genuine insight, end with a question to drive comments.",
    "all": "Create a full social media content package. Label each section clearly: TWITTER THREAD, TWITTER POST, INSTAGRAM CAPTION, LINKEDIN POST.",
}


class SocialAgent(BaseAgent):
    name = "social"

    def run(self, state: OrchestratorState) -> dict:
        try:
            context = state.get("context") or {}
            platform = context.get("platform", "all")
            research_results = context.get("research_results", "")

            search_context = ""
            if context.get("search_web"):
                results = search_web(state["input"], max_results=3)
                search_context = format_search_results(results)

            instructions = PLATFORM_INSTRUCTIONS.get(platform, PLATFORM_INSTRUCTIONS["all"])
            user_prompt = f"Platform: {platform}\nInstructions: {instructions}\n\nTopic/Brief:\n{state['input']}"
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


_agent = SocialAgent()


def run(state: OrchestratorState) -> dict:
    return _agent.run(state)
