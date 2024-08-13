from flask import request, jsonify, Blueprint
from app.agents.base_agent import ChatAgent, CodingAgent
from app.agents.chat_session import ChatSession
from app.agents.silent_agent import SilentAgent
from app.agents.action_organizer_agent import ActionOrganizerAgent
from app.models.base_model import ModelFactory
from app.memory.long_term_memory import LongTermMemory
from config.ai_providers_config import ai_providers_config
from app.workspace.workspace_manager import WorkspaceManager
from app.web.web_manager import WebManager

# Store chat sessions
chat_sessions = {}
workspace_manager = WorkspaceManager()
web_manager = WebManager()

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
        action_organizer_agent = ActionOrganizerAgent(strong_model, silent_agent)
        print("Action organizer agent created")
        chat_session = ChatSession(silent_agent, vocal_agent, action_organizer_agent)
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

@routes.route('/create_workspace', methods=['POST'])
def create_workspace():
    data = request.get_json()
    workspace_name = data.get('workspace_name')
    if not workspace_name:
        return jsonify({"error": "Workspace name is required"}), 400
    
    try:
        workspace_id = workspace_manager.create_workspace(workspace_name)
        return jsonify({"workspace_id": workspace_id}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create workspace: {str(e)}"}), 500

@routes.route('/get_workspace/<workspace_id>', methods=['GET'])
def get_workspace(workspace_id):
    try:
        workspace = workspace_manager.get_workspace(workspace_id)
        return jsonify(workspace), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get workspace: {str(e)}"}), 404

@routes.route('/update_workspace/<workspace_id>', methods=['PUT'])
def update_workspace(workspace_id):
    data = request.get_json()
    try:
        updated_workspace = workspace_manager.update_workspace(workspace_id, data)
        return jsonify(updated_workspace), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update workspace: {str(e)}"}), 400

@routes.route('/delete_workspace/<workspace_id>', methods=['DELETE'])
def delete_workspace(workspace_id):
    try:
        workspace_manager.delete_workspace(workspace_id)
        return jsonify({"message": "Workspace deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete workspace: {str(e)}"}), 400

@routes.route('/list_workspaces', methods=['GET'])
def list_workspaces():
    try:
        workspaces = workspace_manager.list_workspaces()
        return jsonify(workspaces), 200
    except Exception as e:
        return jsonify({"error": f"Failed to list workspaces: {str(e)}"}), 500

@routes.route('/add_file/<workspace_id>', methods=['POST'])
def add_file_to_workspace(workspace_id):
    data = request.get_json()
    file_name = data.get('file_name')
    file_content = data.get('file_content')
    if not file_name or not file_content:
        return jsonify({"error": "File name and content are required"}), 400
    try:
        workspace_manager.add_file_to_workspace(workspace_id, file_name, file_content)
        return jsonify({"message": "File added successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add file: {str(e)}"}), 400

@routes.route('/get_file/<workspace_id>/<file_name>', methods=['GET'])
def get_file_from_workspace(workspace_id, file_name):
    try:
        file = workspace_manager.get_file_from_workspace(workspace_id, file_name)
        return jsonify(file), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get file: {str(e)}"}), 404

@routes.route('/update_file/<workspace_id>/<file_name>', methods=['PUT'])
def update_file_in_workspace(workspace_id, file_name):
    data = request.get_json()
    new_content = data.get('new_content')
    if not new_content:
        return jsonify({"error": "New content is required"}), 400
    try:
        workspace_manager.update_file_in_workspace(workspace_id, file_name, new_content)
        return jsonify({"message": "File updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update file: {str(e)}"}), 400

@routes.route('/delete_file/<workspace_id>/<file_name>', methods=['DELETE'])
def delete_file_from_workspace(workspace_id, file_name):
    try:
        workspace_manager.delete_file_from_workspace(workspace_id, file_name)
        return jsonify({"message": "File deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete file: {str(e)}"}), 400

@routes.route('/list_files/<workspace_id>', methods=['GET'])
def list_files_in_workspace(workspace_id):
    try:
        files = workspace_manager.list_files_in_workspace(workspace_id)
        return jsonify(files), 200
    except Exception as e:
        return jsonify({"error": f"Failed to list files: {str(e)}"}), 400

@routes.route('/update_configuration/<workspace_id>', methods=['PUT'])
def update_workspace_configuration(workspace_id):
    data = request.get_json()
    try:
        workspace_manager.update_workspace_configuration(workspace_id, data)
        return jsonify({"message": "Configuration updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update configuration: {str(e)}"}), 400

@routes.route('/get_configuration/<workspace_id>', methods=['GET'])
def get_workspace_configuration(workspace_id):
    try:
        configuration = workspace_manager.get_workspace_configuration(workspace_id)
        return jsonify(configuration), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get configuration: {str(e)}"}), 400

# Web tab routes
@routes.route('/get_web_action_history', methods=['GET'])
def get_web_action_history():
    try:
        history = web_manager.get_action_history()
        return jsonify({"actions": history}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get web action history: {str(e)}"}), 500

@routes.route('/web_search', methods=['POST'])
def web_search():
    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({"error": "Query is required"}), 400
    try:
        results = web_manager.perform_search(query)
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to perform web search: {str(e)}"}), 500

@routes.route('/load_url_content', methods=['POST'])
def load_url_content():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    try:
        content = web_manager.load_url_content(url)
        return jsonify({"content": content}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to load URL content: {str(e)}"}), 500

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
