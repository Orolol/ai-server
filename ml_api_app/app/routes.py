from flask import request, jsonify, Blueprint
from app.agents.base_agent import ChatAgent, CodingAgent
from app.models.base_model import WeakModel, StrongModel

routes = Blueprint('routes', __name__)


def init_routes(app):
    app.register_blueprint(routes)


def create_model(model_type, model_name_or_key):
    if model_type == "openai":
        return WeakModel("openai")
    elif model_type == "weak":
        return WeakModel(model_name_or_key)
    elif model_type == "strong":
        return StrongModel(model_name_or_key)
    else:
        raise ValueError("Invalid model type")


def create_agent(agent_type, model):
    if agent_type == "chat":
        return ChatAgent(model)
    elif agent_type == "coding":
        return CodingAgent(model)
    else:
        raise ValueError("Invalid agent type")


@routes.route('/predict', methods=['POST'])
def predict_route():
    data = request.get_json()
    print(f"Received data: {data}")

    try:
        model = create_model(data.get("model_type", "strong"),
                             data.get("model_name_or_key"))
        agent = create_agent(data.get("agent_type"), model)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    response = agent.act(data)
    print(f"Agent response: {response}")
    return jsonify(response)
