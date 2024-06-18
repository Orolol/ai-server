from app.models.base_model import OpenAIModel, HuggingFaceModel
from app.agents.base_agent import CodingAgent, ChatAgent


def predict(data, model_type="openai", model_name_or_key=None, agent_type=None):
    try:
        if model_type == "openai":
            if model_name_or_key is None:
                raise ValueError("model_name_or_key must be provided for OpenAI models")
            if model_name_or_key == "gpt-4":
                model = OpenAIModel(api_key=os.getenv("OPENAI_API_KEY_GPT4"))
            elif model_name_or_key == "gpt-3.5":
                model = OpenAIModel(api_key=os.getenv("OPENAI_API_KEY_GPT35"))
            else:
                raise ValueError(f"Unsupported OpenAI model: {model_name_or_key}")
        elif model_type == "huggingface":
            model = HuggingFaceModel(model_name=model_name_or_key)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

        return model.predict(data)
    except Exception as e:
        import traceback
        return {"error": str(e), "stack": traceback.format_exc()}
