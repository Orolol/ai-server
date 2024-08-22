import os
from flask import request, jsonify, Blueprint, send_from_directory, current_app, g
from flask_cors import CORS
from app.agents.vocal_agent import VocalAgent
from app.agents.coding_agent import CodingAgent
from app.agents.chat_session import ChatSession
from app.agents.silent_agent import SilentAgent
from app.agents.action_organizer_agent import ActionOrganizerAgent
from app.agents.web_agent import WebAgent
from app.models.base_model import ModelFactory
from app.memory.long_term_memory import LongTermMemory
from config.ai_providers_config import ai_providers_config
from app.session_storage import SessionStorage
from datetime import datetime
from flask import g

# Create a single instance of LongTermMemory
long_term_memory = LongTermMemory()

# Store chat sessions in memory
current_session = None
session_storage = SessionStorage()
session_ids = session_storage.list_sessions()

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
        return VocalAgent(model, system_message=system_message)
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
    global current_session
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
            print(f"Chat session created with ID: {chat_session.session_id} and creation date: {chat_session.creation_date}")

        current_session = chat_session
        if chat_session.session_id not in session_ids:
            session_ids.append(chat_session.session_id)
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
        "strong_model": chat_session.vocal_agent.model.model_name,
        "weak_model": chat_session.silent_agent.model.model_name,
        "ai_provider": ai_provider,
        "conversation_history_length": len(chat_session.conversation_history)
    })


@routes.route('/send_message', methods=['POST'])
def send_message():
    global current_session
    data = request.get_json()
    print(f"Received data to send message: {data}")

    chatsessionsid = data.get("chatsessionsid")
    message = data.get("message")
    
    if not chatsessionsid or chatsessionsid not in session_ids:
        return jsonify({"error": "Invalid or missing chatsessionsid"}), 400
    
    if not message:
        return jsonify({"error": "Missing message"}), 400

    if current_session is None or current_session.session_id != chatsessionsid:
        current_session = session_storage.load_session(chatsessionsid)

    response = current_session.process_input({"prompt": message})
    print(f"Chat session response: {response}")

    # Save the updated session
    session_storage.save_session(current_session)

    return jsonify({"response": response})

@routes.route('/save_session', methods=['POST'])
def save_session():
    global current_session
    data = request.get_json()
    chatsessionsid = data.get("chatsessionsid")
    
    if not chatsessionsid or chatsessionsid not in session_ids:
        return jsonify({"error": "Invalid or missing chatsessionsid"}), 400

    if current_session is None or current_session.session_id != chatsessionsid:
        current_session = session_storage.load_session(chatsessionsid)

    session_storage.save_session(current_session)
    
    return jsonify({"message": "Session saved successfully"}), 200

@routes.route('/load_session/<session_id>', methods=['GET'])
def load_session(session_id):
    global current_session
    chat_session = session_storage.load_session(session_id)
    
    if not chat_session:
        return jsonify({"error": "Session not found"}), 404

    current_session = chat_session
    if session_id not in session_ids:
        session_ids.append(session_id)
    
    return jsonify({
        "chatsessionsid": chat_session.session_id,
        "creation_date": getattr(chat_session, 'creation_date', datetime.now().isoformat()),
        "strong_model": chat_session.vocal_agent.model.model_name if hasattr(chat_session, 'vocal_agent') else 'N/A',
        "weak_model": chat_session.silent_agent.model.model_name if hasattr(chat_session, 'silent_agent') else 'N/A',
        "ai_provider": chat_session.ai_provider if hasattr(chat_session, 'ai_provider') else 'N/A',
        "conversation_history_length": len(chat_session.conversation_history) if hasattr(chat_session, 'conversation_history') else 0
    }), 200

@routes.route('/list_sessions', methods=['GET'])
def list_sessions():
    print("Listing sessions", session_ids)
    session_details = []
    for session_id in session_ids:
            session_details.append({
                "id": session_id,
            })
    return jsonify({"sessions": session_details}), 200

@routes.route('/delete_session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    global current_session
    session_storage.delete_session(session_id)
    if session_id in session_ids:
        session_ids.remove(session_id)
    if current_session and current_session.session_id == session_id:
        current_session = None
    return jsonify({"message": "Session deleted successfully"}), 200

@routes.route('/get_messages/<chatsessionsid>', methods=['GET'])
def get_messages(chatsessionsid):
    global current_session
    if not chatsessionsid or chatsessionsid not in session_ids:
        return jsonify({"error": "Invalid or missing chatsessionsid"}), 400

    if current_session is None or current_session.session_id != chatsessionsid:
        current_session = session_storage.load_session(chatsessionsid)

    messages = current_session.get_messages()
    return jsonify({"messages": messages}), 200

@routes.route('/clear_memory', methods=['POST'])
def clear_memory():
    try:
        long_term_memory.clear_memory()
        return jsonify({"message": "Memory cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to clear memory: {str(e)}"}), 500

# Web tab routes
@routes.route('/get_web_action_history/<chatsessionsid>', methods=['GET'])
def get_web_action_history(chatsessionsid):
    global current_session
    if not chatsessionsid or chatsessionsid not in session_ids:
        return jsonify({"error": "Invalid or missing chatsessionsid"}), 400
    try:
        if current_session is None or current_session.session_id != chatsessionsid:
            current_session = session_storage.load_session(chatsessionsid)
        history = current_session.get_web_action_history()
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
        memory_id = long_term_memory.add_memory(memory_content)
        return jsonify({"memory_id": memory_id}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add memory: {str(e)}"}), 500

@routes.route('/get_memory/<memory_id>', methods=['GET'])
def get_memory(memory_id):
    try:
        memory_content = long_term_memory.get_memory(memory_id)
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
        long_term_memory.update_memory(memory_id, new_content)
        return jsonify({"message": "Memory updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update memory: {str(e)}"}), 400

@routes.route('/delete_memory/<memory_id>', methods=['DELETE'])
def delete_memory(memory_id):
    try:
        long_term_memory.delete_memory(memory_id)
        return jsonify({"message": "Memory deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete memory: {str(e)}"}), 400

@routes.route('/search_memories', methods=['GET'])
def search_memories():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    try:
        results = long_term_memory.search_memories(query)
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to search memories: {str(e)}"}), 500

@routes.route('/get_memory_action_history/<chatsessionsid>', methods=['GET'])
def get_memory_action_history(chatsessionsid):
    global current_session
    if not chatsessionsid or chatsessionsid not in session_ids:
        return jsonify({"error": "Invalid or missing chatsessionsid"}), 400
    try:
        if current_session is None or current_session.session_id != chatsessionsid:
            current_session = session_storage.load_session(chatsessionsid)
        history = current_session.get_memory_action_history()
        # Convert the history to a list of dictionaries
        formatted_history = [
            {
                "type": entry["type"],
                "timestamp": entry["timestamp"],
                "details": entry["details"]
            }
            for entry in history
        ]
        return jsonify({"history": formatted_history}), 200
    except Exception as e:
        print(f"Error in get_memory_action_history: {str(e)}")
        return jsonify({"error": f"Failed to get memory action history: {str(e)}"}), 500

@routes.route('/start_web_session', methods=['POST'])
def start_web_session():
    global current_session
    data = request.get_json()
    ai_provider = data.get("ai_provider", "openai")
    start_url = data.get("start_url")
    prompt = data.get("prompt")

    if not start_url or not prompt:
        return jsonify({"error": "start_url and prompt are required"}), 400

    try:
        strong_model = ModelFactory.create_model(ai_provider, "strong")
        web_agent = WebAgent(strong_model)
        chat_session = ChatSession(web_agent, web_agent, None, ai_provider)
        chat_session.creation_date = datetime.now().isoformat()

        current_session = chat_session
        session_ids.append(chat_session.session_id)
        session_storage.save_session(chat_session)

        return jsonify({
            "chatsessionsid": chat_session.session_id,
            "creation_date": chat_session.creation_date,
            "ai_provider": ai_provider
        })
    except Exception as e:
        return jsonify({"error": f"Failed to start web session: {str(e)}"}), 500

@routes.route('/execute_web_action', methods=['POST'])
def execute_web_action():
    global current_session
    data = request.get_json()
    chatsessionsid = data.get("chatsessionsid")
    
    if not chatsessionsid or chatsessionsid not in session_ids:
        return jsonify({"error": "Invalid or missing chatsessionsid"}), 400

    if current_session is None or current_session.session_id != chatsessionsid:
        current_session = session_storage.load_session(chatsessionsid)

    try:
        result = current_session.vocal_agent.act(data)
        session_storage.save_session(current_session)
        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to execute web action: {str(e)}"}), 500

@routes.route('/get_web_action_history/<chatsessionsid>', methods=['GET'])
def get_web_action_history(chatsessionsid):
    global current_session
    if not chatsessionsid or chatsessionsid not in session_ids:
        return jsonify({"error": "Invalid or missing chatsessionsid"}), 400
    try:
        if current_session is None or current_session.session_id != chatsessionsid:
            current_session = session_storage.load_session(chatsessionsid)
        history = current_session.vocal_agent.execution_history
        return jsonify({"history": history}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get web action history: {str(e)}"}), 500
