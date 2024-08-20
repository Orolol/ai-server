import json
import os
from app.agents.chat_session import ChatSession

class SessionStorage:
    def __init__(self, storage_dir='session_storage'):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_session(self, session):
        filename = f"{self.storage_dir}/{session.session_id}.json"
        with open(filename, 'w') as f:
            json.dump(session.to_dict(), f)

    def load_session(self, session_id, ai_provider):
        filename = f"{self.storage_dir}/{session_id}.json"
        if not os.path.exists(filename):
            return None
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Initialize agents
        strong_model = ModelFactory.create_model(ai_provider, "strong")
        weak_model = ModelFactory.create_model(ai_provider, "weak")
        vocal_agent = ChatAgent(strong_model)
        silent_agent = SilentAgent(memory_db_path="localhost", ai_provider=ai_provider, strength="weak")
        action_organizer_agent = ActionOrganizerAgent(strong_model, silent_agent)
        
        return ChatSession.from_dict(data, silent_agent, vocal_agent, action_organizer_agent)

    def delete_session(self, session_id):
        filename = f"{self.storage_dir}/{session_id}.json"
        if os.path.exists(filename):
            os.remove(filename)

    def list_sessions(self):
        return [f.split('.')[0] for f in os.listdir(self.storage_dir) if f.endswith('.json')]
