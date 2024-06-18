from flask import Flask, request
from dotenv import load_dotenv
import os
from app.routes import init_routes
from app.utils.logger import api_logger
from app.agents.base_agent import ChatSession, CodingAgent, ChatAgent
from app.models.base_model import WeakModel, StrongModel

load_dotenv()

app = Flask(__name__)
init_routes(app)

@app.before_request
def log_request_info():
    api_logger.info(f"Request: {request.method} {request.url} - Body: {request.get_json()}")

# Initialize agents with strong and weak models
strong_model = StrongModel(model_type="openai")
weak_model = WeakModel(model_type="openai")

silent_agent = CodingAgent(model=weak_model)
vocal_agent = ChatAgent(model=strong_model)

# Create a chat session
chat_session = ChatSession(silent_agent=silent_agent, vocal_agent=vocal_agent)

if __name__ == "__main__":
    app.run(debug=True)
