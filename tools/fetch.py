from tavily import TavilyClient
from config import get_settings


def extract_url_content(url: str) -> str:
    """Extract readable content from a URL via Tavily. Returns '' if unavailable."""
    api_key = get_settings().tavily_api_key
    if not api_key:
        return ""
    client = TavilyClient(api_key=api_key)
    try:
        result = client.extract(urls=[url])
        results = result.get("results", [])
        return results[0].get("raw_content", "") if results else ""
    except Exception:
        return ""
