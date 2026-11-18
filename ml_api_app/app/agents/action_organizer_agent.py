from app.agents.base_agent import Agent
from app.models.base_model import Model
from app.agents.web_agent import WebAgent
from typing import Dict, Any, List
import json
from jinja2 import Environment, FileSystemLoader
import datetime

class ActionOrganizerAgent(Agent):
    def __init__(self, model: Model, silent_agent, web_agent: WebAgent):
        self.model = model
        self.silent_agent = silent_agent
        self.web_agent = web_agent
        
        self.env = Environment(loader=FileSystemLoader('app/templates'))
        self.update_preprompt()
    
    def update_preprompt(self):
        template = self.env.get_template('action_organizer_agent_preprompt.jinja')
        self.preprompt = template.render({"date": datetime.datetime.now().strftime("%Y-%m-%d")})

    def act(self, data: Dict[str, Any]) -> Dict[str, Any]:
        message = data.get('prompt') or data.get('message')
        if not message:
            raise ValueError("No 'prompt' or 'message' found in the input data")
        actions_result = self.organize_actions(message)
        return actions_result

    def organize_actions(self, message: str) -> Dict[str, Any]:
        actions_result = {}
        all_results = []
        loop_count = 0
        max_loops = 5

        while loop_count < max_loops:
            loop_count += 1
            
            # Combine original message with all previous results
            combined_input = f"{message}\n\nPrevious actions results:\n{json.dumps(all_results, indent=2)}"
            
            analysis = self.analyze_message(combined_input)
            
            if "actions" in analysis:
                for action in analysis["actions"]:
                    print("######################################################")
                    print("ACTION EXCECUTION: ", action)
                    action_result = self.execute_action(action)
                    print("ACTION RESULT: ", action_result)
                    actions_result[action["name"]] = action_result
                    all_results.append({"action": action["name"], "result": action_result})
            
            # Check if we have enough information or can't answer
            if analysis.get("status") == "complete" or analysis.get("status") == "cannot_answer":
                break

        return {
            "actions_result": actions_result,
            "final_status": analysis.get("status", "incomplete"),
            "iterations": loop_count
        }

    def analyze_message(self, message: str) -> Dict[str, Any]:
        self.update_preprompt()  # Ensure the date is current
        analysis_prompt = f"""Analyze this message and determine if any actions are needed: {message}
        """
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
            return {"actions": [], "status": "cannot_answer"}

    def execute_action(self, action: Dict[str, Any]) -> Any:
        action_name = action["name"]
        action_params = action["parameters"]

        if action_name == "memory":
            action_params['type'] = action_params.get('type', 'memory_retrieve')  # Default to retrieve if not specified
            return self.silent_agent.memory_action(action_params)
        elif action_name == "url_lookup":
            return self.silent_agent.url_lookup_action(action_params)
        elif action_name == "Web_search":
            return self.silent_agent.web_search_action(action_params)
        elif action_name == "web_action":
            return self.web_agent.act(action_params)
        else:
            return f"Unknown action: {action_name}"
