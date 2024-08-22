from flask import Flask, request, jsonify
from dotenv import load_dotenv
from app.routes import init_routes
from app.utils.logger import api_logger
from app.workspace.workspace_manager import WorkspaceManager

load_dotenv()

app = Flask(__name__)
print("Initializing Flask app")
init_routes(app)
print("Routes initialized", app.url_map)

# Initialize WorkspaceManager
workspace_manager = WorkspaceManager()
app.config['WORKSPACE_MANAGER'] = workspace_manager


@app.before_request
def log_request_info():
    api_logger.info(
        f"Request: {request.method} {request.url} - Headers: {request.headers} - Body: {request.get_data(as_text=True)}")

@app.route('/get_memory_action_history/<session_id>', methods=['GET'])
def get_memory_action_history(session_id):
    chat_session = workspace_manager.get_chat_session(session_id)
    if chat_session:
        memory_action_history = chat_session.get_memory_action_history()
        return jsonify(memory_action_history)
    else:
        return jsonify({"error": "Chat session not found"}), 404

if __name__ == "__main__":
    print("Starting Flask app")
    app.run(debug=True)
