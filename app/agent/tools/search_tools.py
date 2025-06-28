from typing import List, Dict
from langchain_core.tools import tool
from fastapi.concurrency import run_in_threadpool
import requests

from app.core.config import settings

@tool
async def search_web(query: str, num_results: int = 5) -> List[Dict]:
    """
    Searches the web and returns a list of results, each with a title, link, and snippet.
    """
    try:
        headers = {"X-API-KEY": settings.SERPER_API_KEY, "Content-Type": "application/json"}
        payload = {"q": query, "num": min(num_results, 10)}
        response = await run_in_threadpool(requests.post, "https://google.serper.dev/search", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "organic" not in data: return []
        return [
            {
                "title": r.get('title'), 
                "link": r.get('link'), 
                "snippet": r.get('snippet')
            } 
            for r in data["organic"]
        ]
    except Exception as e:
        return [{"error": f"Web search failed: {e}"}]

@tool 
async def search_news(query: str, num_results: int = 5) -> List[Dict]:
    """
    Searches for news articles and returns a list of results, each with a title, source, date, link, and snippet.
    """
    try:
        headers = {"X-API-KEY": settings.SERPER_API_KEY, "Content-Type": "application/json"}
        payload = {"q": query, "num": min(num_results, 10)}
        response = await run_in_threadpool(requests.post, "https://google.serper.dev/news", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "news" not in data: return []
        return [{"title": a.get('title'), "source": a.get('source'), "date": a.get('date'), "link": a.get('link'), "snippet": a.get('snippet')} for a in data['news']]
    except Exception as e:
        return [{"error": f"News search failed: {e}"}]