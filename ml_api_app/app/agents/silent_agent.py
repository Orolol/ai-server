from app.memory.long_term_memory import LongTermMemory
from app.utils.logger import ai_logger
from bs4 import BeautifulSoup
import requests
import datetime

class SilentAgent:
    def __init__(self, memory_db_path="localhost"):
        self.memory = LongTermMemory(memory_db_path)

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
        ai_logger.info(f"{datetime.datetime.now()} - Memory search results: {results}")
        return results

    def url_lookup_action(self, data):
        url = data.get("url")
        if not url:
            raise ValueError("URL is required for URL_lookup action")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        # Store the scraped content in the vector collection
        self.memory.store_interaction("url_lookup", text, [])
        ai_logger.info(f"{datetime.datetime.now()} - URL lookup content stored: {text[:100]}...")  # Log first 100 chars
        return text
