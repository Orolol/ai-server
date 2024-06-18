from abc import ABC, abstractmethod

class Agent(ABC):
    @abstractmethod
    def act(self, data):
        pass

class CodingAgent(Agent):
    def __init__(self, model):
        self.model = model

    def act(self, data):
        # Implement the logic for coding agent
        return self.model.predict(data)

class ChatAgent(Agent):
    def __init__(self, model):
        self.model = model

    def act(self, data):
        # Implement the logic for chat agent
        return self.model.predict(data)
