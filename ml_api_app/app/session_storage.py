import json
import os
from app.agents.chat_session import ChatSession
from app.models.base_model import ModelFactory
from app.agents.vocal_agent import VocalAgent
from app.agents.silent_agent import SilentAgent
from app.agents.web_agent import WebAgent
from app.agents.action_organizer_agent import ActionOrganizerAgent

class SessionStorage:
    def __init__(self, storage_dir='session_storage'):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_session(self, session):
        filename = f"{self.storage_dir}/{session.session_id}.json"
        with open(filename, 'w') as f:
            json.dump(session.to_dict(), f)

    def load_session(self, session_id):
        print("Loading session", session_id)
        filename = f"{self.storage_dir}/{session_id}.json"
        if not os.path.exists(filename):
            return None
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Initialize agents
        ai_provider = data.get('ai_provider', 'openai')  # Default to 'openai' if not present
        strong_model = ModelFactory.create_model(ai_provider, "strong")
        vocal_agent = VocalAgent(strong_model)
        web_agent = WebAgent(strong_model)
        silent_agent = SilentAgent(memory_db_path="localhost", ai_provider=ai_provider, strength="weak")
        action_organizer_agent = ActionOrganizerAgent(strong_model, silent_agent, web_agent)
        
        return ChatSession.from_dict(data, silent_agent, vocal_agent, action_organizer_agent, ai_provider)

    def delete_session(self, session_id):
        filename = f"{self.storage_dir}/{session_id}.json"
        if os.path.exists(filename):
            os.remove(filename)

    def list_sessions(self):
        return [f.split('.')[0] for f in os.listdir(self.storage_dir) if f.endswith('.json')]
