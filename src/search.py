import os, requests

class SearchResult:
    def __init__(self, title:str, url:str, snippet:str):
        self.title, self.url, self.snippet = title, url, snippet

class SearchClient:
    def __init__(self):
        self.provider = os.getenv("SEARCH_PROVIDER","serpapi").lower()
        self.key = os.getenv("SERPAPI_KEY") if self.provider=="serpapi" else os.getenv("BING_KEY")

    def search(self, q: str):
        if self.provider=="serpapi":
            return self._serpapi(q)
        return self._bing(q)

    def _serpapi(self, q: str):
        url = "https://serpapi.com/search.json"
        params = {"engine":"google","q":q,"hl":"ja","num":5,"api_key":self.key}
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        js = r.json()
        res=[]
        for item in (js.get("organic_results") or [])[:5]:
            res.append(SearchResult(item.get("title",""), item.get("link",""), item.get("snippet","")))
        return res

    def _bing(self, q: str):
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {"Ocp-Apim-Subscription-Key": self.key}
        params = {"q": q, "mkt":"ja-JP", "count":5, "textDecorations":False}
        r = requests.get(url, headers=headers, params=params, timeout=8)
        r.raise_for_status()
        js = r.json()
        res=[]
        for item in (js.get("webPages",{}).get("value") or [])[:5]:
            res.append(SearchResult(item.get("name",""), item.get("url",""), item.get("snippet","")))
        return res
