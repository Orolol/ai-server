from flask import request, jsonify, Blueprint
from app.models.model import predict

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
    prediction = predict(data, model_type=model_type, model_name_or_key=model_name_or_key, agent_type=agent_type)
    print(f"Prediction result: {prediction}")
    return jsonify(prediction)
