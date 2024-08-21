import os
from flask import request, jsonify, Blueprint, send_from_directory, current_app, g
from flask_cors import CORS
from app.agents.base_agent import ChatAgent, CodingAgent
from app.agents.chat_session import ChatSession
from app.agents.silent_agent import SilentAgent
from app.agents.action_organizer_agent import ActionOrganizerAgent
from app.models.base_model import ModelFactory
from app.memory.long_term_memory import LongTermMemory
from config.ai_providers_config import ai_providers_config
from app.session_storage import SessionStorage
from datetime import datetime

# Store chat sessions
chat_sessions = {}
session_storage = SessionStorage()

routes = Blueprint('routes', __name__)


def init_routes(app):
    print("Initializing routes")
    app.register_blueprint(routes)
    CORS(app)  # Enable CORS for all routes

@routes.route('/', defaults={'path': ''})
@routes.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(current_app.static_folder + '/' + path):
        return send_from_directory(current_app.static_folder, path)
    else:
        return send_from_directory(current_app.static_folder, 'index.html')


def create_agent(agent_type, model, system_message=""):
    print(f"Creating agent of type: {agent_type} with model: {model}")
    if agent_type == "chat":
        return ChatAgent(model, system_message=system_message)
    elif agent_type == "coding":
        return CodingAgent(model, system_message=system_message)
    else:
        raise ValueError("Invalid agent type")


@routes.route('/config_options', methods=['GET'])
def config_options():
    ai_providers = ["openai", "anthropic", "huggingface"]
    strengths = ["weak", "medium", "strong"]
    return jsonify({"ai_providers": ai_providers, "strengths": strengths}), 200
@routes.route('/start_chat', methods=['POST'])
def start_chat():
    print("Received request to start chat")
    data = request.get_json()
    print(f"Request data: {data}")

    ai_provider = data.get("ai_provider", "openai")
    system_message = data.get("system_message", "")
    session_id = data.get("session_id")

    try:
        if session_id:
            # Load existing session
            ai_provider = data.get("ai_provider", "openai")
            chat_session = session_storage.load_session(session_id, ai_provider)
            if not chat_session:
                return jsonify({"error": "Session not found"}), 404
            print(f"Loaded existing chat session with ID: {chat_session.session_id}")
        else:
            # Create new session
            print(f"System message: {system_message}")
            print("Creating chat session")
            strong_model = ModelFactory.create_model(ai_provider, "strong")
            print(f"Model created: {ai_provider} (strong) {strong_model.model_name}")
            weak_model = ModelFactory.create_model(ai_provider, "weak")
            print(f"Model created: {ai_provider} (weak) {weak_model.model_name}")
            vocal_agent = create_agent("chat", strong_model, system_message)
            print("Vocal agent created")
            silent_agent = SilentAgent(
                memory_db_path="localhost", ai_provider=ai_provider, strength="weak")
            print("Silent agent created")
            action_organizer_agent = ActionOrganizerAgent(strong_model, silent_agent)
            print("Action organizer agent created")
            chat_session = ChatSession(silent_agent, vocal_agent, action_organizer_agent)
            chat_session.creation_date = datetime.now().isoformat()
            chat_session.strong_model = strong_model.model_name
            chat_session.weak_model = weak_model.model_name
            print(f"Chat session created with ID: {chat_session.session_id}")

        chat_sessions[chat_session.session_id] = chat_session
        # Save the session
        session_storage.save_session(chat_session)
    except ValueError as e:
        print(f"Error starting chat: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": f"Unexpected error occurred: {str(e)}"}), 500

    return jsonify({
        "chatsessionsid": chat_session.session_id,
        "creation_date": chat_session.creation_date,
        "strong_model": chat_session.strong_model,
        "weak_model": chat_session.weak_model
    })


@routes.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    print(f"Received data to send message: {data}")

    chatsessionsid = data.get("chatsessionsid")
    message = data.get("message")
    
    if not chatsessionsid or chatsessionsid not in chat_sessions:
        return jsonify({"error": "Invalid or missing chatsessionsid"}), 400
    
    if not message:
        return jsonify({"error": "Missing message"}), 400

    chat_session = chat_sessions[chatsessionsid]
    response = chat_session.process_input({"prompt": message})
    print(f"Chat session response: {response}")

    # Save the updated session
    session_storage.save_session(chat_session)

    return jsonify({"response": response})

@routes.route('/save_session', methods=['POST'])
def save_session():
    data = request.get_json()
    chatsessionsid = data.get("chatsessionsid")
    
    if not chatsessionsid or chatsessionsid not in chat_sessions:
        return jsonify({"error": "Invalid or missing chatsessionsid"}), 400

    chat_session = chat_sessions[chatsessionsid]
    session_storage.save_session(chat_session)
    
    return jsonify({"message": "Session saved successfully"}), 200

@routes.route('/load_session/<session_id>', methods=['GET'])
def load_session(session_id):
    ai_provider = request.args.get('ai_provider', 'openai')  # Default to 'openai' if not provided
    chat_session = session_storage.load_session(session_id, ai_provider)
    
    if not chat_session:
        return jsonify({"error": "Session not found"}), 404

    chat_sessions[chat_session.session_id] = chat_session
    
    return jsonify({
        "chatsessionsid": chat_session.session_id,
        "creation_date": getattr(chat_session, 'creation_date', 'N/A'),
        "strong_model": getattr(chat_session, 'strong_model', 'N/A'),
        "weak_model": getattr(chat_session, 'weak_model', 'N/A')
    }), 200

@routes.route('/list_sessions', methods=['GET'])
def list_sessions():
    sessions = session_storage.list_sessions()
    session_details = []
    for session in sessions:
        ai_provider = "openai"  # Default provider
        chat_session = session_storage.load_session(session, ai_provider)
        if chat_session:
            session_details.append({
                "id": chat_session.session_id,
                "creation_date": getattr(chat_session, 'creation_date', 'N/A'),
                "strong_model": getattr(chat_session, 'strong_model', 'N/A'),
                "weak_model": getattr(chat_session, 'weak_model', 'N/A')
            })
    return jsonify({"sessions": session_details}), 200

@routes.route('/delete_session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    session_storage.delete_session(session_id)
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    return jsonify({"message": "Session deleted successfully"}), 200

@routes.route('/get_messages/<chatsessionsid>', methods=['GET'])
def get_messages(chatsessionsid):
    if not chatsessionsid or chatsessionsid not in chat_sessions:
        return jsonify({"error": "Invalid or missing chatsessionsid"}), 400

    chat_session = chat_sessions[chatsessionsid]
    messages = chat_session.get_messages()
    return jsonify({"messages": messages}), 200

@routes.route('/clear_memory', methods=['POST'])
def clear_memory():
    try:
        memory = LongTermMemory()
        memory.clear_memory()
        return jsonify({"message": "Memory cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to clear memory: {str(e)}"}), 500

# Web tab routes
@routes.route('/get_web_action_history/<chatsessionsid>', methods=['GET'])
def get_web_action_history(chatsessionsid):
    if not chatsessionsid or chatsessionsid not in chat_sessions:
        return jsonify({"error": "Invalid or missing chatsessionsid"}), 400

    try:
        chat_session = chat_sessions[chatsessionsid]
        history = chat_session.get_web_action_history()
        return jsonify({"actions": history}), 200
    except Exception as e:
        print(f"Failed to get web action history: {str(e)}")
        return jsonify({"error": f"Failed to get web action history: {str(e)}"}), 500
# 
# @routes.route('/web_search', methods=['POST'])
# def web_search():
#     data = request.get_json()
#     query = data.get('query')
#     if not query:
#         return jsonify({"error": "Query is required"}), 400
#     try:
#         results = web_manager.perform_search(query)
#         return jsonify({"results": results}), 200
#     except Exception as e:
#         return jsonify({"error": f"Failed to perform web search: {str(e)}"}), 500
# 
# @routes.route('/load_url_content', methods=['POST'])
# def load_url_content():
#     data = request.get_json()
#     url = data.get('url')
#     if not url:
#         return jsonify({"error": "URL is required"}), 400
#     try:
#         content = web_manager.load_url_content(url)
#         return jsonify({"content": content}), 200
#     except Exception as e:
#         return jsonify({"error": f"Failed to load URL content: {str(e)}"}), 500

# Memory tab routes
@routes.route('/add_memory', methods=['POST'])
def add_memory():
    data = request.get_json()
    memory_content = data.get('content')
    if not memory_content:
        return jsonify({"error": "Memory content is required"}), 400
    try:
        memory = LongTermMemory()
        memory_id = memory.add_memory(memory_content)
        return jsonify({"memory_id": memory_id}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add memory: {str(e)}"}), 500

@routes.route('/get_memory/<memory_id>', methods=['GET'])
def get_memory(memory_id):
    try:
        memory = LongTermMemory()
        memory_content = memory.get_memory(memory_id)
        return jsonify({"content": memory_content}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get memory: {str(e)}"}), 404

@routes.route('/update_memory/<memory_id>', methods=['PUT'])
def update_memory(memory_id):
    data = request.get_json()
    new_content = data.get('content')
    if not new_content:
        return jsonify({"error": "New memory content is required"}), 400
    try:
        memory = LongTermMemory()
        memory.update_memory(memory_id, new_content)
        return jsonify({"message": "Memory updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update memory: {str(e)}"}), 400

@routes.route('/delete_memory/<memory_id>', methods=['DELETE'])
def delete_memory(memory_id):
    try:
        memory = LongTermMemory()
        memory.delete_memory(memory_id)
        return jsonify({"message": "Memory deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete memory: {str(e)}"}), 400

@routes.route('/search_memories', methods=['GET'])
def search_memories():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    try:
        memory = LongTermMemory()
        results = memory.search_memories(query)
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to search memories: {str(e)}"}), 500

@routes.route('/get_memory_action_history', methods=['GET'])
def get_memory_action_history():
    try:
        memory = LongTermMemory()
        history = memory.get_action_history()
        return jsonify({"history": history}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get memory action history: {str(e)}"}), 500
