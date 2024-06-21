import uuid

class ChatSession:
    def __init__(self, silent_agent, vocal_agent):
        self.session_id = str(uuid.uuid4())
        self.silent_agent = silent_agent
        self.vocal_agent = vocal_agent

    def process_input(self, data):
        # Analyze the message using SilentAgent
        analysis_result = self.silent_agent.analyze_message(data['prompt'])
        actions_result = ""
        # Check if any actions are needed based on the analysis
        if analysis_result.get("actions"):
            for action in analysis_result["actions"]:
                if action["name"] == "memory":
                    actions_result += f"After a memory search, the result is here: >> {self.silent_agent.memory_action(action['parameters'])} <<"

                elif action["name"] == "url_lookup":
                    actions_result += f"Here are the results of the URL lookup: >> {self.silent_agent.url_lookup_action(action['parameters'])} <<"

        # Enrich the data with the preprompt and conversation history
        enriched_data = {
            "prompt": f"{self.vocal_agent.preprompt} {data['prompt']} {actions_result}",
            "conversation_history": self.vocal_agent.conversation_history
        }

        # Send the enriched data to the VocalAgent
        response = self.vocal_agent.act(enriched_data)
        return response
