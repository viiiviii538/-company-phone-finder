import os
import time
from dataclasses import dataclass
from typing import List
import requests


@dataclass
class Result:
    title: str
    url: str
    snippet: str


class SearchClient:
    """Simple search client for SerpAPI or Bing Web Search API."""

    def __init__(self, provider: str):
        self.provider = provider.lower()
        if self.provider not in {"serpapi", "bing"}:
            raise ValueError("provider must be 'serpapi' or 'bing'")
        self.api_key = os.getenv("SERPAPI_KEY") if self.provider == "serpapi" else os.getenv("BING_KEY")
        self.session = requests.Session()
        self.last_request = 0.0

    def _rate_limit(self):
        elapsed = time.time() - self.last_request
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self.last_request = time.time()

    def search(self, query: str) -> List[Result]:
        self._rate_limit()
        if self.provider == "serpapi":
            url = "https://serpapi.com/search.json"
            params = {"q": query, "engine": "bing", "api_key": self.api_key}
            r = self.session.get(url, params=params, timeout=8)
            r.raise_for_status()
            data = r.json()
            items = data.get("organic_results", [])
            return [Result(title=i.get("title", ""), url=i.get("link", ""), snippet=i.get("snippet", "")) for i in items]
        else:
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            params = {"q": query}
            r = self.session.get(url, params=params, headers=headers, timeout=8)
            r.raise_for_status()
            data = r.json()
            items = data.get("webPages", {}).get("value", [])
            return [Result(title=i.get("name", ""), url=i.get("url", ""), snippet=i.get("snippet", "")) for i in items]
