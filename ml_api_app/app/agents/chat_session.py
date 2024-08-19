import uuid
from typing import List, Dict, Any

class ChatSession:
    def __init__(self, silent_agent, vocal_agent, action_organizer_agent):
        self.session_id = str(uuid.uuid4())
        self.silent_agent = silent_agent
        self.vocal_agent = vocal_agent
        self.action_organizer_agent = action_organizer_agent
        self.web_action_history: List[Dict[str, Any]] = []

    def process_input(self, data):
        # Use ActionOrganizerAgent to analyze and execute actions
        actions_result = self.action_organizer_agent.act(data)

        print(("#################################"))
        print("Actions result: ", actions_result)

        # Format the actions_result for the vocal agent and update web action history
        invisible_info = ""
        for action_name, result in actions_result.items():
            invisible_info += f"[INVISIBLE TO USER] {action_name.capitalize()} result: {result} [/INVISIBLE]\n"
            if action_name in ["Web_search", "url_lookup"]:
                self.web_action_history.append({
                    "type": action_name,
                    "details": result,
                    "timestamp": datetime.datetime.now().isoformat()
                })

        # Enrich the data with the preprompt, user's prompt, and invisible actions result
        enriched_data = {
            "prompt": f"{self.vocal_agent.preprompt}\n\n[INVISIBLE TO USER] The following information is not visible to the user and should be used to inform your response without directly referencing it:\n{invisible_info}[/INVISIBLE]\n\nUser's message: {data['prompt']}\n\nPlease respond to the user based on the above information:",
            "conversation_history": self.vocal_agent.conversation_history
        }

        print("Enriched data: ", enriched_data)

        # Send the enriched data to the VocalAgent
        response = self.vocal_agent.act(enriched_data)
        return response

    def get_web_action_history(self) -> List[Dict[str, Any]]:
        return self.web_action_history