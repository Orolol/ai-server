from app.models.base_model import OpenAIModel, HuggingFaceModel

# Example usage
def predict(data, model_type="openai", model_name_or_key=None):
    if model_type == "openai":
        model = OpenAIModel(api_key=model_name_or_key)
    elif model_type == "huggingface":
        model = HuggingFaceModel(model_name=model_name_or_key)
    else:
        raise ValueError("Unsupported model type")

    return {"prediction": model.predict(data)}
