from app.memory.long_term_memory import LongTermMemory
from abc import ABC, abstractmethod
from app.utils.logger import ai_logger
from jinja2 import Environment, FileSystemLoader
import datetime
import os
import re


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


class CodingAgent(Agent):
    def __init__(self, model, memory_db_path="localhost", preprompt="", system_message=""):
        print(
            f"Initializing CodingAgent with model: {model}, memory_db_path: {memory_db_path}, preprompt: {preprompt}, system_message: {system_message}")
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('preprompt_template.jinja')
        self.preprompt = template.render()
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
        print("current path: ", os.getcwd())
        env = Environment(loader=FileSystemLoader('app/templates'))
        template = env.get_template('preprompt_template.jinja')
        self.preprompt = template.render()
        self.memory = LongTermMemory(memory_db_path)
        self.conversation_history = [
            {"role": "system", "content": system_message}]
        self.model = model
        self.system_message = system_message

    def act(self, data):
        # Remove hidden parts from the user's prompt
        visible_prompt = self.remove_hidden_parts(data["prompt"])
        
        # Append only the visible part to the conversation history
        self.conversation_history.append(
            {"role": "user", "content": visible_prompt})
        
        # Prepare data for the model
        data["conversation_history"] = self.conversation_history
        data["prompt"] = visible_prompt  # Use the visible prompt for prediction
        
        # Get prediction from the model
        prediction = self.model.predict(data)
        
        # Process the prediction to ensure no hidden parts are included
        visible_prediction = self.remove_hidden_parts(prediction)
        
        # Append the visible prediction to the conversation history
        self.conversation_history.append(
            {"role": "assistant", "content": visible_prediction})
        
        # Store the interaction in memory
        self.memory.store_interaction(
            "chat", visible_prediction, data.get("keywords", []))
        
        return visible_prediction

    def remove_hidden_parts(self, text):
        # Remove parts enclosed in [INVISIBLE TO USER] tags
        return re.sub(r'\[INVISIBLE TO USER\].*?\[/INVISIBLE\]', '', text, flags=re.DOTALL)


