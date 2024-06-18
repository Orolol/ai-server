import chromadb
from datetime import datetime

class LongTermMemory:
    def __init__(self, host="localhost", port=8000):
        self.client = chromadb.HttpClient(host=host, port=port)
        self.collection = self.client.create_collection("interactions")

    def store_interaction(self, agent_type, interaction, keywords):
        date = datetime.now().isoformat()
        self.collection.add(
            documents=[interaction],
            metadatas=[{"agent_type": agent_type, "keywords": keywords, "date": date}],
            ids=[f"{agent_type}_{date}"]
        )

    def retrieve_interactions(self, keywords):
        results = self.collection.query(
            query_texts=keywords,
            n_results=10
        )
        return results
