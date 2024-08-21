from app.agents.base_agent import ModelAgent
from app.utils.logger import ai_logger
from jinja2 import Environment, FileSystemLoader
import datetime
import os
import re

class VocalAgent(ModelAgent):
    def __init__(self, model, memory_db_path="localhost", preprompt="", system_message=""):
        super().__init__(model, memory_db_path, preprompt, system_message)
        print("current path: ", os.getcwd())
        env = Environment(loader=FileSystemLoader('app/templates'))
        template = env.get_template('preprompt_template.jinja')
        self.preprompt = template.render()
        self.conversation_history = [
            {"role": "system", "content": system_message}]

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
        
        ai_logger.info(
            f"{datetime.datetime.now()} - Model: {self.model.__class__.__name__}, Agent: {self.__class__.__name__}, Input: {data}, Interaction: {visible_prediction}")
        
        return visible_prediction

    def remove_hidden_parts(self, text):
        # Remove parts enclosed in [INVISIBLE TO USER] tags
        return re.sub(r'\[INVISIBLE TO USER\].*?\[/INVISIBLE\]', '', text, flags=re.DOTALL)
