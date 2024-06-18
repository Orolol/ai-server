from flask import request, jsonify
from app.models.model import predict

def init_routes(app):
    @app.route('/predict', methods=['POST'])
    def predict_route():
        data = request.get_json()
        prediction = predict(data)
        return jsonify(prediction)
