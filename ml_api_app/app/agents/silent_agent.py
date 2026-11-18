from app.memory.long_term_memory import LongTermMemory
from app.utils.logger import ai_logger
from bs4 import BeautifulSoup
import requests
import datetime
from app.models.base_model import ModelFactory, Model
from jinja2 import Environment, FileSystemLoader
import json
from typing import Dict, Any, List
from app.utils.brave_search import BraveSearch
from app.agents.base_agent import ModelAgent
from app.agents.web_agent import WebAgent


class SilentAgent(ModelAgent):
    def __init__(self, memory_db_path: str = "localhost", ai_provider: str = "openai", strength: str = "weak"):
        model = ModelFactory.create_model(ai_provider, strength)
        super().__init__(model, memory_db_path)
        self.brave_search = BraveSearch()

    def act(self, data: Dict[str, Any]) -> Any:
        action = data.get("action")

        if action == "memory":
            return self.memory_action(data)
        elif action == "url_lookup":
            return self.url_lookup_action(data)
        elif action == "Web_search":
            return self.web_search_action(data)
        else:
            raise ValueError(f"Unknown action: {action}")

    def memory_action(self, data: Dict[str, Any]) -> Any:
        action_type = data.get('type')
        if not action_type:
            raise ValueError("Memory action type is missing or None")
        if action_type == 'memory_store':
            return self.memory.store_interaction(data.get('key'), data.get('value'), data.get('tags', []))
        elif action_type == 'memory_retrieve':
            return self.memory.retrieve_interactions(data.get('search_terms'))
        else:
            raise ValueError(f"Unknown memory action type: {action_type}")

    def web_search_action(self, data: Dict[str, Any]) -> str:
        ai_logger.info(f"Web search action initiated with data: {data}")
        query = data.get("query")
        if not query:
            raise ValueError("Query is required for Web_search action")
        
        detailed_summary = self.brave_search.get_detailed_summary(query)
        
        result = detailed_summary.get('summary')
        
        # If no summary is available from Brave Search API, generate one using the model
        if not result:
            summary_prompt = f"Summarize the following search results for the query. Please keep urls and try to keep as much information needed to answer the query.: '{query}'\n\n"
            for search_result in detailed_summary['results']:
                summary_prompt += f"Title: {search_result['title']}\nDescription: {search_result['description']}\nURL: {search_result['url']}\n\n"
            result = self.model.predict({"prompt": summary_prompt})
        
        # Store the search action
        self.memory.store_interaction(
            "web_search",
            json.dumps({
                "query": query,
                "result": result
            }),
            [query]
        )
        ai_logger.info(f"Web search results and summary stored for query: {query}")

        return result

    def url_lookup_action(self, data: Dict[str, Any]) -> str:
        ai_logger.info(f"URL lookup action initiated with data: {data}")
        url = data.get("url")
        if not url:
            raise ValueError("URL is required for URL_lookup action")
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()

        summary_prompt = f"Summarize the main content of the following webpage:\n\n{text[:5000]}"  # Limit to first 5000 characters
        summary = self.model.predict({"prompt": summary_prompt})

        # Store the URL lookup action
        self.memory.store_interaction(
            "url_lookup",
            json.dumps({
                "url": url,
                "summary": summary
            }),
            [url]
        )
        ai_logger.info(f"URL lookup summary stored for URL: {url}")

        return summary

