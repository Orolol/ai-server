from app.models.base_model import WeakModel, StrongModel
from flask import request, jsonify, Blueprint
from app.agents.base_agent import ChatAgent, CodingAgent, ChatSession
import uuid

# Store chat sessions
chat_sessions = {}

routes = Blueprint('routes', __name__)


def init_routes(app):
    print("Initializing routes")
    app.register_blueprint(routes)


def create_model(model_type, model_name_or_key):
    print(
        f"Creating model of type: {model_type} with key: {model_name_or_key}")
    if model_type == "openai":
        return WeakModel("openai")
    elif model_type == "weak":
        return WeakModel(model_name_or_key)
    elif model_type == "strong":
        return StrongModel(model_name_or_key)
    else:
        raise ValueError("Invalid model type")


def create_agent(agent_type, model):
    print(f"Creating agent of type: {agent_type} with model: {model}")
    if agent_type == "chat":
        return ChatAgent(model)
    elif agent_type == "coding":
        return CodingAgent(model)
    else:
        raise ValueError("Invalid agent type")


@routes.route('/start_chat', methods=['POST'])
def start_chat():
    print("Received request to start chat")
    print("Received request to send message")
    data = request.get_json()
    print(f"Request data: {data}")
    print(f"Request data: {data}")
    print(f"Received data to start chat: {data}")

    try:
        print("Creating chat session")
        vocal_model = create_model("strong", "gpt-4o")
        silent_model = create_model("weak", "gpt-3.5")
        vocal_agent = create_agent("chat", vocal_model)
        silent_agent = create_agent("chat", silent_model)
        chat_session = ChatSession(silent_agent, vocal_agent)
        chat_sessions[chat_session.session_id] = chat_session
    except ValueError as e:
        print(f"Error starting chat: {e}")
        return jsonify({"error": str(e)}), 400

    return jsonify({"chatsessionsid": chat_session.session_id})


@routes.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    print(f"Received data to send message: {data}")

    chatsessionsid = data.get("chatsessionsid")
    if not chatsessionsid or chatsessionsid not in chat_sessions:
        return jsonify({"error": "Invalid or missing chatsessionsid"}), 400

    chat_session = chat_sessions[chatsessionsid]
    response = chat_session.process_input(data)
    print(f"Chat session response: {response}")
    return jsonify(response)
