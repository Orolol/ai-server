from flask import request, jsonify, Blueprint
from app.agents.base_agent import ChatAgent, CodingAgent

routes = Blueprint('routes', __name__)


def init_routes(app):
    app.register_blueprint(routes)


@routes.route('/predict', methods=['POST'])
def predict_route():
    data = request.get_json()
    print(f"Received data: {data}")
    model_type = data.get("model_type", "openai")
    model_name_or_key = data.get("model_name_or_key")
    agent_type = data.get("agent_type")
    if agent_type == "chat":
        agent = ChatAgent(model_name_or_key)
    elif agent_type == "coding":
        agent = CodingAgent(model_name_or_key)
    else:
        return jsonify({"error": "Invalid agent type"}), 400

    response = agent.act(data)
    print(f"Agent response: {response}")
    return jsonify(response)
