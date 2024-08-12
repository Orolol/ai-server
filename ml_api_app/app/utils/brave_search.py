import requests
import os
from typing import Dict, Any

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
