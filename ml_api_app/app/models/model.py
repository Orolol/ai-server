from app.models.base_model import OpenAIModel, HuggingFaceModel
from app.agents.base_agent import CodingAgent, ChatAgent

def predict(data, model_type="openai", model_name_or_key=None, agent_type=None):
    try:
        if model_type == "openai":
            model = OpenAIModel(api_key=model_name_or_key)
        elif model_type == "huggingface":
            model = HuggingFaceModel(model_name=model_name_or_key)
        else:
            raise ValueError("Unsupported model type")

        if agent_type == "coding":
            agent = CodingAgent(model, memory_db_path="memory_db")
        elif agent_type == "chat":
            agent = ChatAgent(model, memory_db_path="memory_db")
        else:
            raise ValueError(f"Unsupported agent type: {agent_type}. Supported types are 'coding' and 'chat'.")

        prediction = agent.act(data)
        print(f"Prediction: {prediction}")
        return {"prediction": prediction}
    except Exception as e:
        return {"error": str(e)}
