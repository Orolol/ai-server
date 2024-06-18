from flask import Flask, request
from dotenv import load_dotenv
import os
from app.routes import init_routes, routes
from app.utils.logger import api_logger

load_dotenv()

app = Flask(__name__)
app.register_blueprint(routes)

@app.before_request
def log_request_info():
    api_logger.info(f"Request: {request.method} {request.url} - Body: {request.get_json()}")

from app.agents.base_agent import ChatSession, CodingAgent, ChatAgent
from app.models.model import predict

# Initialize agents
silent_agent = CodingAgent(model=predict)
vocal_agent = ChatAgent(model=predict)

# Create a chat session
chat_session = ChatSession(silent_agent=silent_agent, vocal_agent=vocal_agent)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    response = chat_session.process_input(data)
    return response
    app.run(debug=True)
