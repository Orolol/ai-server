import requests
import os
from typing import Dict, Any, List

class BraveSearch:
    BASE_URL = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self):
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not self.api_key:
            raise ValueError("BRAVE_SEARCH_API_KEY environment variable is not set")

    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        params = {
            "q": query,
            **kwargs
        }
        response = requests.get(self.BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_summary(self, summary_key: str) -> Dict[str, Any]:
        summarizer_url = "https://api.search.brave.com/res/v1/summarizer/search"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        params = {
            "key": summary_key
        }
        response = requests.get(summarizer_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_detailed_summary(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        search_results = self.search(query, count=num_results)
        
        detailed_summary = {
            "query": query,
            "results": [],
            "summary": ""
        }

        for result in search_results.get("web", {}).get("results", []):
            result_summary = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "description": result.get("description", ""),
            }
            detailed_summary["results"].append(result_summary)

        if "summaryKey" in search_results:
            summary = self.get_summary(search_results["summaryKey"])
            detailed_summary["summary"] = summary.get("summary", "No summary available.")


        return detailed_summary
