from app.models.base_model import WeakModel, StrongModel
from flask import request, jsonify, Blueprint
from app.agents.base_agent import ChatAgent, CodingAgent
from app.agents.chat_session import ChatSession
from app.agents.silent_agent import SilentAgent
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


def create_agent(agent_type, model, system_message=""):
    print(f"Creating agent of type: {agent_type} with model: {model}")
    if agent_type == "chat":
        return ChatAgent(model, system_message=system_message)
    elif agent_type == "coding":
        return CodingAgent(model, system_message=system_message)
    else:
        raise ValueError("Invalid agent type")


@routes.route('/start_chat', methods=['POST'])
def start_chat():
    print("Received request to start chat")
    data = request.get_json()
    print(f"Request data: {data}")

    vocal_model_type = data.get("vocal_model_type", "strong")
    vocal_model_name = data.get("vocal_model_name", "openai")
    silent_model_type = data.get("silent_model_type", "weak")
    silent_model_name = data.get("silent_model_name", "openai")
    system_message = data.get("system_message", "")

    try:
        print(f"System message: {system_message}")
        print("Creating chat session")
        vocal_model = create_model(vocal_model_type, vocal_model_name)
        print(f"Vocal model created: {vocal_model_type} - {vocal_model_name}")
        silent_model = create_model(silent_model_type, silent_model_name)
        print(f"Silent model created: {silent_model_type} - {silent_model_name}")
        vocal_agent = create_agent("chat", vocal_model, system_message)
        print("Vocal agent created")
        silent_agent = SilentAgent(
            memory_db_path="localhost", model_type=silent_model_name)
        print("Silent agent created")
        chat_session = ChatSession(silent_agent, vocal_agent)
        print(f"Chat session created with ID: {chat_session.session_id}")
        chat_sessions[chat_session.session_id] = chat_session
    except ValueError as e:
        print(f"Error starting chat: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": f"Unexpected error occurred: {str(e)}"}), 500

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
    return jsonify({"response": response})
