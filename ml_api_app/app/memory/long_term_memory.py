import chromadb
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


class LongTermMemory:
    def __init__(self, host=None, port=None):
        try:
            host = host or os.getenv("CHROMADB_HOST", "localhost")
            port = port or int(os.getenv("CHROMADB_PORT", 8000))
            logger.info(f"Connecting to ChromaDB at {host}:{port}")
            print(f"Connecting to ChromaDB at {host}:{port}")
            self.client = chromadb.HttpClient(host=host, port=port)
            collections = [col.name for col in self.client.list_collections()]
            if "interactions" not in collections:
                self.collection = self.client.create_collection("interactions")
            else:
                self.collection = self.client.get_collection("interactions")
            logger.info(f"Connected to ChromaDB at {host}:{port}")
        except Exception as e:
            logger.error(
                f"Failed to connect to ChromaDB at {host}:{port} - {str(e)}", exc_info=True)
            raise

    def store_interaction(self, agent_type, interaction, keywords):
        try:
            date = datetime.now().isoformat()
            self.collection.add(
                documents=[interaction],
                metadatas=[{"agent_type": agent_type,
                            "keywords": ", ".join(keywords), "date": date}],
                ids=[f"{agent_type}_{date}"]
            )
            logger.info(
                f"Stored interaction for agent type {agent_type} with keywords {keywords}")
        except Exception as e:
            logger.error(
                f"Failed to store interaction - {str(e)}", exc_info=True)
            raise

    def retrieve_interactions(self, keywords):
        try:
            results = self.collection.query(
                query_texts=keywords,
                n_results=10
            )
            logger.info(f"Retrieved interactions for keywords {keywords}")
            return results
        except Exception as e:
            logger.error(
                f"Failed to retrieve interactions - {str(e)}", exc_info=True)
            raise
