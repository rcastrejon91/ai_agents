def web_search(query: str, max_results: int = 5) -> dict:
    import os
    from tavily import TavilyClient
    try:
        client = TavilyClient(os.environ.get("TAVILY_API_KEY", ""))
        resp = client.search(query=query, max_results=max_results, search_depth="advanced")
        results = resp.get("results", [])
        return {
            "result": "Found " + str(len(results)) + " results for: " + query,
            "items": [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")[:400],
                }
                for r in results
            ],
            "query": query,
        }
    except Exception as e:
        return {"error": str(e)}
