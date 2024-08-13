from flask import request, jsonify, Blueprint
from app.agents.base_agent import ChatAgent, CodingAgent
from app.agents.chat_session import ChatSession
from app.agents.silent_agent import SilentAgent
from app.agents.action_organizer_agent import ActionOrganizerAgent
from app.models.base_model import ModelFactory
from app.memory.long_term_memory import LongTermMemory
from config.ai_providers_config import ai_providers_config
from app.workspace.workspace_manager import WorkspaceManager

# Store chat sessions
chat_sessions = {}
workspace_manager = WorkspaceManager()

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
