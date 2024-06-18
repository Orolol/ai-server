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
            agent = CodingAgent(model, memory_db_path="localhost")
        elif agent_type == "chat":
            agent = ChatAgent(model, memory_db_path="localhost")
        else:
            raise ValueError(
                f"Unsupported agent type: {agent_type}. Supported types are 'coding' and 'chat'.")

        prediction = agent.act({"prompt": data["data"]})
        print(f"Prediction: {prediction}")
        from app.utils.logger import ai_logger
        import datetime

        ai_logger.info(f"{datetime.datetime.now()} - Model: {model.__class__.__name__}, Agent: {agent.__class__.__name__}, Interaction: {prediction}")
        
        return {"prediction": prediction}
    except Exception as e:
        import traceback
        return {"error": str(e), "stack": traceback.format_exc()}
