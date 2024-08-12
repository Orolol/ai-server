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


class SilentAgent(ModelAgent):
    def __init__(self, memory_db_path: str = "localhost", ai_provider: str = "openai", strength: str = "weak"):
        model = ModelFactory.create_model(ai_provider, strength)
        super().__init__(model, memory_db_path)

        env = Environment(loader=FileSystemLoader('app/templates'))
        template = env.get_template('silent_agent_preprompt.jinja')
        self.preprompt = template.render({"date": datetime.datetime.now()})
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

    def web_search_action(self, data: Dict[str, Any]) -> str:
        ai_logger.info(f"Web search action initiated with data: {data}")
        query = data.get("query")
        if not query:
            raise ValueError("Query is required for Web_search action")
        
        detailed_summary = self.brave_search.get_detailed_summary(query)
        
        print("DETAILED SUMMARY: ", detailed_summary)   
        
        result = detailed_summary.get('summary', "No summary available.")
        
        print("RESULT: ", result)

        # Store each search result individually
        for search_result in detailed_summary['results']:
            self.memory.store_interaction(
                "web_search_result",
                json.dumps({
                    "query": query,
                    "title": search_result['title'],
                    "description": search_result['description'],
                    "url": search_result['url']
                }),
                [query, search_result['title']]
            )

        # Store the overall summary
        self.memory.store_interaction("web_search_summary", result, [query])
        ai_logger.info(f"Web search results and summary stored for query: {query}")

        # If no summary is available, generate one using the model
        if result == "No summary available.":
            summary_prompt = f"Summarize the following search results for the query: '{query}'\n\n"
            for result in detailed_summary['results']:
                summary_prompt += f"Title: {result['title']}\nDescription: {result['description']}\nURL: {result['url']}\n\n"
            result = self.model.predict({"prompt": summary_prompt})

        return result

    def memory_action(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        search_terms = data.get("search_terms", "")
        keywords = data.get("keywords", [])
        date = data.get("date")
        results = self.memory.search_interactions(search_terms, keywords, date)
        ai_logger.info(
            f"{datetime.datetime.now()} - Memory search results: {results}")
        return results

    def url_lookup_action(self, data: Dict[str, Any]) -> str:
        ai_logger.info(f"URL lookup action initiated with data: {data}")
        url = data.get("url")
        query = data.get("query")
        if not url:
            raise ValueError("URL is required for URL_lookup action")
        if not query:
            raise ValueError("Query is required for URL_lookup action")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()

        summary_prompt = f"In the following text, extract and summarize information in relation the user query. Query : '{query}'\n\nText: {text}"
        summary = self.model.predict({"prompt": summary_prompt})

        self.memory.store_interaction("url_lookup", summary, [])
        ai_logger.info(f"URL lookup summary stored: {summary[:100]}...")

        return summary
