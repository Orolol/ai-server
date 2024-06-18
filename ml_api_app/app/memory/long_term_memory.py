import chromadb
from datetime import datetime

class LongTermMemory:
    def __init__(self, db_path):
        self.client = chromadb.Client(path=db_path)

    def store_interaction(self, agent_type, interaction, keywords):
        date = datetime.now().isoformat()
        self.client.insert({
            "agent_type": agent_type,
            "interaction": interaction,
            "keywords": keywords,
            "date": date
        })

    def retrieve_interactions(self, keywords):
        return self.client.query({
            "keywords": keywords
        })
