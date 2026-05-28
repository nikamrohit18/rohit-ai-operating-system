from orchestrator.state import OrchestratorState

VALID_AGENTS = {"research", "content", "seo", "digital_twin", "social", "youtube"}

KEYWORD_MAP = {
    "research": ["research", "analyze", "investigate", "explore", "summarize", "find out", "what is"],
    "content": ["write", "post", "article", "blog", "linkedin", "content", "draft", "caption", "rewrite"],
    "seo": ["seo", "optimize", "ranking", "keyword", "backlink", "geo", "schema", "sitemap"],
    "digital_twin": ["twin", "chat", "voice", "who is rohit", "about rohit", "rohit's"],
    "social": ["twitter", "tweet", "instagram", "social media", "thread", "hashtag", "x post"],
    "youtube": ["youtube", "video script", "video title", "video description", "yt", "thumbnail", "video idea"],
}


def route_task(state: OrchestratorState) -> str:
    task_type = state.get("task_type", "").lower().strip()
    if task_type in VALID_AGENTS:
        return task_type

    text = state.get("input", "").lower()
    for agent, keywords in KEYWORD_MAP.items():
        if any(kw in text for kw in keywords):
            return agent

    return "research"
