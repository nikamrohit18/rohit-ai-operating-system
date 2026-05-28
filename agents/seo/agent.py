from agents.base import BaseAgent
from orchestrator.state import OrchestratorState
from tools.search import search_web, format_search_results
from tools.fetch import extract_url_content

SYSTEM_PROMPT = """You are an SEO and GEO (Generative Engine Optimization) specialist for rohitnikam.tech.
Optimize Rohit's online presence for both traditional search engines and AI-powered search (ChatGPT, Perplexity, Claude).

When given SERP data, analyze what the top-ranking pages cover and identify gaps Rohit can own.
When given a page to audit, provide specific on-page fixes with exact copy suggestions.
When given content to optimize, rewrite title tags, meta descriptions, headings, and add schema markup.

Always output:
1. Keyword analysis (search intent, difficulty, related terms)
2. Content gaps vs top competitors
3. On-page recommendations (title tag, meta description, H1/H2 structure, schema markup)
4. GEO recommendations (how to structure content so AI models cite Rohit as an authority)
5. Internal linking opportunities for rohitnikam.tech

Be specific and actionable — no generic advice."""


class SEOAgent(BaseAgent):
    name = "seo"

    def run(self, state: OrchestratorState) -> dict:
        try:
            context = state.get("context") or {}
            keyword = context.get("keyword") or state["input"]
            target_url = context.get("target_url", "")
            content_to_optimize = context.get("content", "")

            # SERP analysis for the keyword
            serp_results = search_web(keyword, max_results=7)
            serp_context = format_search_results(serp_results)
            sources = [r.get("url") for r in serp_results if r.get("url")]

            # Optional: audit a specific page
            url_context = ""
            if target_url:
                page_content = extract_url_content(target_url)
                if page_content:
                    url_context = f"\n\n## Target Page to Audit: {target_url}\n{page_content[:6000]}"
                    sources.append(target_url)

            user_prompt = f"SEO task: {state['input']}\nPrimary keyword: {keyword}"
            if serp_context:
                user_prompt += f"\n\n{serp_context}"
            if url_context:
                user_prompt += url_context
            if content_to_optimize:
                user_prompt += f"\n\n## Content to Optimize\n{content_to_optimize}"

            output = self.call_claude(
                system=SYSTEM_PROMPT,
                user=user_prompt,
                max_tokens=4096,
            )
            return {"output": output, "status": "completed", "sources": sources}
        except Exception as e:
            return {"output": None, "status": "failed", "error": str(e)}


_agent = SEOAgent()


def run(state: OrchestratorState) -> dict:
    return _agent.run(state)
