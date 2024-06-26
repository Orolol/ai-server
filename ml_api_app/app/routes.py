from flask import request, jsonify, Blueprint
from app.agents.base_agent import ChatAgent, CodingAgent
from app.agents.chat_session import ChatSession
from app.agents.silent_agent import SilentAgent
from app.models.base_model import ModelFactory
from app.memory.long_term_memory import LongTermMemory
from config.ai_providers_config import ai_providers_config

# Store chat sessions
chat_sessions = {}

routes = Blueprint('routes', __name__)


def init_routes(app):
    print("Initializing routes")
    app.register_blueprint(routes)


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

    ai_provider = data.get("ai_provider", "openai")
    system_message = data.get("system_message", "")

    try:
        print(f"System message: {system_message}")
        print("Creating chat session")
        strong_model = ModelFactory.create_model(ai_provider, "strong")
        print(
            f"Model created: {ai_provider} (strong) {strong_model.model_name}")
        weak_model = ModelFactory.create_model(ai_provider, "weak")
        print(f"Model created: {ai_provider} (weak) {weak_model.model_name}")
        vocal_agent = create_agent("chat", strong_model, system_message)
        print("Vocal agent created")
        silent_agent = SilentAgent(
            memory_db_path="localhost", ai_provider=ai_provider, strength="weak")
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

@routes.route('/clear_memory', methods=['POST'])
def clear_memory():
    try:
        memory = LongTermMemory()
        memory.clear_memory()
        return jsonify({"message": "Memory cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to clear memory: {str(e)}"}), 500
