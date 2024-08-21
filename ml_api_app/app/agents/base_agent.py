from abc import ABC, abstractmethod
from app.memory.long_term_memory import LongTermMemory

class Agent(ABC):
    @abstractmethod
    def act(self, data):
        pass

class ModelAgent(Agent):
    def __init__(self, model, memory_db_path="localhost", preprompt="", system_message=""):
        self.model = model
        self.memory = LongTermMemory(memory_db_path)
        self.conversation_history = []
        self.preprompt = preprompt
        self.system_message = system_message

    def act(self, data):
        raise NotImplementedError("Subclasses must implement this method")


