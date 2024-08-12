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
                    actions_result += f"[INVISIBLE TO USER] Memory search result: {self.silent_agent.memory_action(action['parameters'])} [/INVISIBLE]\n"
                elif action["name"] == "url_lookup":
                    actions_result += f"[INVISIBLE TO USER] URL lookup result: {self.silent_agent.url_lookup_action(action['parameters'])} [/INVISIBLE]\n"
                elif action["name"] == "Web_search":
                    actions_result += f"[INVISIBLE TO USER] Web search result: {self.silent_agent.web_search_action(action['parameters'])} [/INVISIBLE]\n"

        # Enrich the data with the preprompt, user's prompt, and invisible actions result
        enriched_data = {
            "prompt": f"{self.vocal_agent.preprompt}\n\n[INVISIBLE TO USER] The following information is not visible to the user and should be used to inform your response without directly referencing it:\n{actions_result}[/INVISIBLE]\n\nUser's message: {data['prompt']}\n\nPlease respond to the user based on the above information:",
            "conversation_history": self.vocal_agent.conversation_history
        }
        
        print("Enriched data: ", enriched_data)

        # Send the enriched data to the VocalAgent
        response = self.vocal_agent.act(enriched_data)
        return response
