from app.memory.long_term_memory import LongTermMemory
from abc import ABC, abstractmethod


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
        print(f"Prediction by {self.__class__.__name__}: {prediction}")
        self.memory.store_interaction(
            "coding", prediction, data.get("keywords", []))
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
