import chromadb
from datetime import datetime
import os
import logging
import json
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class LongTermMemory:
    def __init__(self, host=None, port=None):
        self.host = host or os.getenv("CHROMADB_HOST", "localhost")
        self.port = port or int(os.getenv("CHROMADB_PORT", 8000))
        logger.info(f"Attempting to connect to ChromaDB at {self.host}:{self.port}")
        print(f"Attempting to connect to ChromaDB at {self.host}:{self.port}")
        
        self.client = None
        self.collection = None
        self._connect_and_initialize()

    def _connect_and_initialize(self):
        try:
            self.client = chromadb.HttpClient(host=self.host, port=self.port)
            self._initialize_collection()
            logger.info(f"Successfully connected to ChromaDB at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB at {self.host}:{self.port} - {str(e)}", exc_info=True)
            raise ConnectionError(f"Unable to establish connection with ChromaDB: {str(e)}")

    def _initialize_collection(self):
        if not self.client:
            raise RuntimeError("ChromaDB client is not initialized")

        try:
            print("STATE OF THE CLIENT", self.client)
            try:
                self.collection = self.client.create_collection("long_term_memory")
                logger.info("Created 'long_term_memory' collection.")
            except Exception as create_error:
                if "already exists" in str(create_error):
                    logger.info("'long_term_memory' collection already exists. Retrieving it.")
                    self.collection = self.client.get_collection("long_term_memory")
                else:
                    raise create_error
        except Exception as e:
            logger.error(f"Failed to initialize collection - {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to initialize ChromaDB collection: {str(e)}")

    def _ensure_connection(self):
        if not self.client or not self.collection:
            logger.warning("ChromaDB connection lost. Attempting to reconnect...")
            self._connect_and_initialize()

    def store_interaction(self, agent_type, interaction, keywords):
        self._ensure_connection()
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

    def search_interactions(self, search_terms, keywords, date=None, n_results=10):
        try:
            query = " ".join(search_terms)
            filter_criteria = {}

            if keywords:
                filter_criteria["keywords"] = {"$in": keywords}

            if date is not None:
                date_filter = {"date": {"$gte": date.isoformat()}}
                if filter_criteria:
                    filter_criteria = {"$and": [filter_criteria, date_filter]}
                else:
                    filter_criteria = date_filter

            print(query, filter_criteria)
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_criteria if filter_criteria else None
            )
            logger.info(
                f"Searched interactions with terms: {search_terms}, keywords: {keywords}, date: {date}")
            return results
        except Exception as e:
            logger.error(
                f"Failed to search interactions - {str(e)}", exc_info=True)
            raise

    def clear_memory(self):
        try:
            # Get all document IDs
            all_ids = self.collection.get()["ids"]
            
            # Delete all documents using their IDs
            if all_ids:
                self.collection.delete(ids=all_ids)
                logger.info(f"Cleared {len(all_ids)} interactions from the memory")
            else:
                logger.info("No interactions to clear from the memory")
        except Exception as e:
            logger.error(f"Failed to clear memory - {str(e)}", exc_info=True)
            raise

    def retrieve_search_results(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        try:
            results = self.collection.query(
                query_texts=[query],
                where={"$and": [{"agent_type": "web_search_result"}]},
                n_results=n_results
            )
            search_results = []
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                search_result = json.loads(doc)
                search_result['score'] = metadata['distance']
                search_results.append(search_result)
            logger.info(f"Retrieved {len(search_results)} search results for query: {query}")
            return search_results
        except Exception as e:
            logger.error(f"Failed to retrieve search results - {str(e)}", exc_info=True)
            raise
