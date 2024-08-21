import uuid
from typing import List, Dict, Any
import json
import datetime
import re

class ChatSession:
    def __init__(self, silent_agent, vocal_agent, action_organizer_agent, session_id=None, conversation_history=None):
        self.session_id = session_id or str(uuid.uuid4())
        self.silent_agent = silent_agent
        self.vocal_agent = vocal_agent
        self.action_organizer_agent = action_organizer_agent
        self.web_action_history: List[Dict[str, Any]] = []
        self.memory_action_history: List[Dict[str, Any]] = []
        if conversation_history:
            self.vocal_agent.conversation_history = conversation_history

    def to_dict(self):
        return {
            'session_id': self.session_id,
            'conversation_history': self.vocal_agent.conversation_history,
            'web_action_history': self.web_action_history,
            'memory_action_history': self.memory_action_history
        }

    @classmethod
    def from_dict(cls, data, silent_agent, vocal_agent, action_organizer_agent):
        if vocal_agent is None:
            raise ValueError("vocal_agent must be provided and cannot be None")
        session = cls(silent_agent, vocal_agent, action_organizer_agent, 
                      session_id=data['session_id'], 
                      conversation_history=data['conversation_history'])
        session.web_action_history = data['web_action_history']
        session.memory_action_history = data.get('memory_action_history', [])
        return session

    def process_input(self, data):
        # Use ActionOrganizerAgent to analyze and execute actions
        actions_result = self.action_organizer_agent.act(data)

        print(("#################################"))
        print("Actions result: ", actions_result)

        # Format the actions_result for the vocal agent and update action histories
        invisible_info = ""
        for action_name, result in actions_result.items():
            invisible_info += f"[INVISIBLE TO USER] {action_name.capitalize()} result: {result} [/INVISIBLE TO USER]\n"
            action_entry = {
                "type": action_name,
                "details": result,
                "timestamp": datetime.datetime.now().isoformat()
            }
            if action_name in ["Web_search", "url_lookup"]:
                self.web_action_history.append(action_entry)
            elif action_name in ["memory_store", "memory_retrieve"]:
                self.memory_action_history.append(action_entry)

        # Enrich the data with the preprompt, user's prompt, and invisible actions result
        enriched_data = {
            "prompt": f"{self.vocal_agent.preprompt}\n\n[INVISIBLE TO USER] The following information is not visible to the user and should be used to inform your response without directly referencing it:\n{invisible_info}\n\nUser's message: [/INVISIBLE TO USER]{data['prompt']}\n\nPlease respond to the user based on the above information:",
            "conversation_history": self.vocal_agent.conversation_history
        }

        print("Enriched data: ", enriched_data)

        # Send the enriched data to the VocalAgent
        response = self.vocal_agent.act(enriched_data)

        # Remove hidden parts from the response
        visible_response = self.remove_hidden_parts(response)
        return visible_response

    def remove_hidden_parts(self, text):
        return re.sub(r'\[INVISIBLE TO USER\].*?\[/INVISIBLE TO USER\]', '', text, flags=re.DOTALL)

    def get_web_action_history(self) -> List[Dict[str, Any]]:
        return self.web_action_history

    def get_memory_action_history(self) -> List[Dict[str, Any]]:
        return self.memory_action_history

    def get_messages(self) -> List[Dict[str, Any]]:
        """
        Retrieve the conversation history.
        
        Returns:
            List[Dict[str, Any]]: A list of message dictionaries, each containing 'role' and 'content'.
        """
        return self.vocal_agent.conversation_history
