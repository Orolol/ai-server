from app.memory.long_term_memory import LongTermMemory
from app.utils.logger import ai_logger
from bs4 import BeautifulSoup
import requests
import datetime
from app.models.base_model import ModelFactory, Model
from jinja2 import Environment, FileSystemLoader
import json
from typing import Dict, Any


class SilentAgent:
    def __init__(self, memory_db_path: str = "localhost", ai_provider: str = "openai", strength: str = "weak"):
        self.memory = LongTermMemory(memory_db_path)

        env = Environment(loader=FileSystemLoader('app/templates'))
        template = env.get_template('silent_agent_preprompt.jinja')
        self.preprompt = template.render({"date": datetime.datetime.now()})
        self.model: Model = ModelFactory.create_model(ai_provider, strength)

    def act(self, data):
        action = data.get("action")
        if action == "Memory":
            return self.memory_action(data)
        elif action == "URL_lookup":
            return self.url_lookup_action(data)
        else:
            raise ValueError("Unknown action")

    def memory_action(self, data):
        search_terms = data.get("search_terms", "")
        keywords = data.get("keywords", [])
        date = data.get("date", None)
        # Implement the logic to search in the vectorial database
        # This is a placeholder implementation
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

        # Use the model to summarize the text using the query
        summary_prompt = f"Summarize the following text in relation to this query: '{query}'\n\nText: {text}"
        summary = self.model.predict([{"role": "user", "content": summary_prompt}])

        # Store the summarized content in the vector collection
        self.memory.store_interaction("url_lookup", summary, [])
        ai_logger.info(f"URL lookup summary stored: {summary[:100]}...")

        return summary

    def analyze_message(self, message: str) -> Dict[str, Any]:
        """
        Analyze the user message to determine if any actions are needed.
        """
        ai_logger.info(f"Analyzing message: {message[:50]}...")
        analysis_result = self.model.predict([
            {"role": "system", "content": self.preprompt},
            {"role": "user", "content": f"Analyze this message: {message}"}
        ])
        ai_logger.info(f"Analysis result: {analysis_result[:100]}...")

        # Convert the JSON string to a Python dictionary
        try:
            return json.loads(analysis_result)
        except json.JSONDecodeError:
            ai_logger.error(f"Failed to parse analysis result as JSON: {analysis_result}")
            return {}
