from app.models.base_model import OpenAIModel, HuggingFaceModel
from app.agents.base_agent import CodingAgent, ChatAgent

def predict(data, model_type="openai", model_name_or_key=None, agent_type=None):
    if model_type == "openai":
        model = OpenAIModel(api_key=model_name_or_key)
    elif model_type == "huggingface":
        model = HuggingFaceModel(model_name=model_name_or_key)
    else:
        raise ValueError("Unsupported model type")

    if agent_type == "coding":
        agent = CodingAgent(model)
    elif agent_type == "chat":
        agent = ChatAgent(model)
    else:
        raise ValueError("Unsupported agent type")

    return {"prediction": agent.act(data)}
