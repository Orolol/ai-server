import json
import os

class SessionStorage:
    def __init__(self, storage_dir='session_storage'):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_session(self, session):
        filename = f"{self.storage_dir}/{session.session_id}.json"
        with open(filename, 'w') as f:
            json.dump(session.to_dict(), f)

    def load_session(self, session_id, silent_agent, vocal_agent, action_organizer_agent):
        filename = f"{self.storage_dir}/{session_id}.json"
        if not os.path.exists(filename):
            return None
        with open(filename, 'r') as f:
            data = json.load(f)
        return ChatSession.from_dict(data, silent_agent, vocal_agent, action_organizer_agent)

    def delete_session(self, session_id):
        filename = f"{self.storage_dir}/{session_id}.json"
        if os.path.exists(filename):
            os.remove(filename)

    def list_sessions(self):
        return [f.split('.')[0] for f in os.listdir(self.storage_dir) if f.endswith('.json')]
