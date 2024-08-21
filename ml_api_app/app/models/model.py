from app.models.base_model import ModelFactory
import logging

logger = logging.getLogger(__name__)

def predict(data, provider="openai", strength="weak"):
    try:
        model = ModelFactory.create_model(provider, strength)
        return model.predict(data)
    except Exception as e:
        logger.error(f"Error in predict function: {str(e)}", exc_info=True)
        return {"error": "An error occurred while processing your request. Please try again later."}
