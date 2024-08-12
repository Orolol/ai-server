from app.agents.base_agent import Agent
from app.models.base_model import Model
from typing import Dict, Any, List
import json
from jinja2 import Environment, FileSystemLoader
import datetime

class ActionOrganizerAgent(Agent):
    def __init__(self, model: Model, silent_agent):
        self.model = model
        self.silent_agent = silent_agent
        
        self.env = Environment(loader=FileSystemLoader('app/templates'))
        self.update_preprompt()
    
    def update_preprompt(self):
        template = self.env.get_template('silent_agent_preprompt.jinja')
        self.preprompt = template.render({"date": datetime.datetime.now().strftime("%Y-%m-%d")})

    def act(self, data: Dict[str, Any]) -> Dict[str, Any]:
        message = data['prompt']
        actions_result = self.organize_actions(message)
        return actions_result

    def organize_actions(self, message: str) -> Dict[str, Any]:
        analysis = self.analyze_message(message)
        actions_result = {}

        if "actions" in analysis:
            for action in analysis["actions"]:
                action_result = self.execute_action(action)
                actions_result[action["name"]] = action_result

                # Check if further actions are needed based on the result
                further_analysis = self.analyze_message(str(action_result))
                if "actions" in further_analysis:
                    for further_action in further_analysis["actions"]:
                        further_result = self.execute_action(further_action)
                        actions_result[further_action["name"]] = further_result

        return actions_result

    def analyze_message(self, message: str) -> Dict[str, Any]:
        self.update_preprompt()  # Ensure the date is current
        analysis_prompt = f"Analyze this message and determine if any actions are needed: {message}"
        analysis_result = self.model.predict({
            "conversation_history": [
                {"role": "system", "content": self.preprompt},
                {"role": "user", "content": analysis_prompt}
            ]
        })
        print("Analysis prompt: ", analysis_prompt)
        print("Analysis result: ", analysis_result)
        
        try:
            return json.loads(analysis_result)
        except json.JSONDecodeError:
            print(f"Failed to parse analysis result as JSON: {analysis_result}")
            return {"actions": []}

    def execute_action(self, action: Dict[str, Any]) -> Any:
        action_name = action["name"]
        action_params = action["parameters"]

        if action_name == "memory":
            return self.silent_agent.memory_action(action_params)
        elif action_name == "url_lookup":
            return self.silent_agent.url_lookup_action(action_params)
        elif action_name == "Web_search":
            return self.silent_agent.web_search_action(action_params)
        else:
            return f"Unknown action: {action_name}"
