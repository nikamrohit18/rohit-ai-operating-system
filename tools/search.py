from tavily import TavilyClient
from config import get_settings


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Search the web using Tavily. Returns [] if API key is not configured."""
    api_key = get_settings().tavily_api_key
    if not api_key:
        return []
    client = TavilyClient(api_key=api_key)
    response = client.search(query, max_results=max_results)
    return response.get("results", [])


def format_search_results(results: list[dict]) -> str:
    if not results:
        return ""
    lines = ["## Web Search Results\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"### [{i}] {r.get('title', 'Untitled')}")
        lines.append(f"Source: {r.get('url', '')}")
        lines.append(r.get("content", "").strip())
        lines.append("")
    return "\n".join(lines)
