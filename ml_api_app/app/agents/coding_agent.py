from app.agents.base_agent import ModelAgent
from app.utils.logger import ai_logger
from jinja2 import Environment, FileSystemLoader
import datetime

class CodingAgent(ModelAgent):
    def __init__(self, model, memory_db_path="localhost", preprompt="", system_message=""):
        super().__init__(model, memory_db_path, preprompt, system_message)
        print(
            f"Initializing CodingAgent with model: {model}, memory_db_path: {memory_db_path}, preprompt: {preprompt}, system_message: {system_message}")
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('preprompt_template.jinja')
        self.preprompt = template.render()

    def act(self, data):
        # Implement the logic for coding agent
        print(f"Data received by {self.__class__.__name__}: {data}")
        prediction = self.model.predict(data)
        print(f"Prediction by {self.__class__.__name__}: {prediction}")
        self.memory.store_interaction(
            "coding", prediction, data.get("keywords", []))

        ai_logger.info(
            f"{datetime.datetime.now()} - Model: {self.model.__class__.__name__}, Agent: {self.__class__.__name__}, Input: {data}, Interaction: {prediction}")

        self.conversation_history.append(
            {"role": "user", "content": data["prompt"]})
        print(f"Updated conversation history: {self.conversation_history}")
        self.conversation_history.append(
            {"role": "assistant", "content": prediction})

        return prediction
