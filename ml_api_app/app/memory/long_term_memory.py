import chromadb
from chromadb.config import Settings
from datetime import datetime

class LongTermMemory:
    def __init__(self, db_path):
        self.client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=db_path))
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
