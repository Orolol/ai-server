from app.models.base_model import ModelFactory

def predict(data, provider="openai", strength="weak"):
    try:
        model = ModelFactory.create_model(provider, strength)
        return model.predict(data)
    except Exception as e:
        import traceback
        return {"error": str(e), "stack": traceback.format_exc()}
