from app.memory.long_term_memory import LongTermMemory
from abc import ABC, abstractmethod
from app.utils.logger import ai_logger
import datetime
import uuid


class Agent(ABC):
    @abstractmethod
    def act(self, data):
        pass


class CodingAgent(Agent):
    def __init__(self, model, memory_db_path="localhost", preprompt="", system_message=""):
        print(f"Initializing CodingAgent with model: {model}, memory_db_path: {memory_db_path}, preprompt: {preprompt}, system_message: {system_message}")
        self.memory = LongTermMemory(memory_db_path)
        self.conversation_history = []
        self.model = model

    def act(self, data):
        # Implement the logic for coding agent
        print(f"Data received by {self.__class__.__name__}: {data}")
        prediction = self.model.predict(data)
        print(f"Prediction by {self.__class__.__name__}: {prediction}")
        self.memory.store_interaction(
            "coding", prediction, data.get("keywords", []))

        ai_logger.info(
            f"{datetime.datetime.now()} - Model: {self.model.__class__.__name__}, Agent: {self.__class__.__name__}, Input: {data}, Interaction: {prediction}")

        print(f"Data received by {self.__class__.__name__}: {data}")
        self.conversation_history.append(
            {"role": "user", "content": data["prompt"]})
        print(f"Updated conversation history: {self.conversation_history}")
        prediction = self.model.predict(data)
        self.conversation_history.append(
            {"role": "assistant", "content": prediction})
        self.memory.store_interaction(
            "chat", prediction, data.get("keywords", []))

        ai_logger.info(
            f"{datetime.datetime.now()} - Model: {self.model.__class__.__name__}, Agent: {self.__class__.__name__}, Input: {data}, Interaction: {prediction}")

        return prediction


class ChatAgent(Agent):
    def __init__(self, model, memory_db_path="localhost", preprompt="", system_message=""):
        self.memory = LongTermMemory(memory_db_path)
        self.conversation_history = [{"role": "system", "content": system_message}]
        self.model = model
        self.preprompt = preprompt
        self.system_message = system_message

    def act(self, data):
        # Implement the logic for chat agent
        self.conversation_history.append(
            {"role": "user", "content": data["prompt"]})
        data["conversation_history"] = self.conversation_history
        prediction = self.model.predict(data)
        self.conversation_history.append(
            {"role": "assistant", "content": prediction})
        self.memory.store_interaction(
            "chat", prediction, data.get("keywords", []))
        return prediction


class ChatSession:
    def __init__(self, silent_agent, vocal_agent, preprompt="", system_message=""):
        self.session_id = str(uuid.uuid4())
        self.silent_agent = silent_agent
        self.vocal_agent = vocal_agent

    def process_input(self, data):
        enriched_data = {"prompt": f"{self.silent_agent.preprompt} {data['prompt']}", "conversation_history": self.silent_agent.conversation_history}
        response = self.vocal_agent.act(enriched_data)
        return response
