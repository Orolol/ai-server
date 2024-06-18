from app.memory.long_term_memory import LongTermMemory
from abc import ABC, abstractmethod
import uuid


class Agent(ABC):
    @abstractmethod
    def act(self, data):
        pass


class CodingAgent(Agent):
    def __init__(self, model, memory_db_path="localhost"):
        self.memory = LongTermMemory(memory_db_path)
        self.model = model

    def act(self, data):
        # Implement the logic for coding agent
        print(f"Data received by {self.__class__.__name__}: {data}")
        prediction = self.model.predict(data)
        from app.utils.logger import ai_logger
        import datetime

        print(f"Prediction by {self.__class__.__name__}: {prediction}")
        self.memory.store_interaction(
            "coding", prediction, data.get("keywords", []))
        
        ai_logger.info(f"{datetime.datetime.now()} - Model: {self.model.__class__.__name__}, Agent: {self.__class__.__name__}, Input: {data}, Interaction: {prediction}")
        
        from app.utils.logger import ai_logger
        import datetime

        self.model.conversation_history.append({"role": "user", "content": data["prompt"]})
        prediction = self.model.predict(data)
        self.model.conversation_history.append({"role": "assistant", "content": prediction})
        self.memory.store_interaction(
            "chat", prediction, data.get("keywords", []))
        
        ai_logger.info(f"{datetime.datetime.now()} - Model: {self.model.__class__.__name__}, Agent: {self.__class__.__name__}, Input: {data}, Interaction: {prediction}")
        
        return prediction


class ChatAgent(Agent):
    def __init__(self, model, memory_db_path="localhost"):
        self.memory = LongTermMemory(memory_db_path)
        self.model = model

    def act(self, data):
        # Implement the logic for chat agent
        self.model.conversation_history.append({"role": "user", "content": data["prompt"]})
        prediction = self.model.predict(data)
        self.model.conversation_history.append({"role": "assistant", "content": prediction})
        self.memory.store_interaction(
            "chat", prediction, data.get("keywords", []))
        return prediction
class ChatSession:
    def __init__(self, silent_agent, vocal_agent):
        self.session_id = str(uuid.uuid4())
        self.silent_agent = silent_agent
        self.vocal_agent = vocal_agent

    def process_input(self, data):
        enriched_data = self.silent_agent.act(data)
        response = self.vocal_agent.act(enriched_data)
        return response
