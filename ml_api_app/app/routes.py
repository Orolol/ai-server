from flask import request, jsonify, Blueprint
from app.models.model import predict

routes = Blueprint('routes', __name__)

def init_routes(app):
    app.register_blueprint(routes)
@routes.route('/predict', methods=['POST'])
def predict_route():
    data = request.get_json()
    print(f"Received data: {data}")
    prediction = predict(data)
    print(f"Prediction result: {prediction}")
    return jsonify(prediction)
