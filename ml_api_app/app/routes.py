from flask import request, jsonify, Blueprint
from app.models.model import predict

routes = Blueprint('routes', __name__)

def init_routes(app):
    app.register_blueprint(routes)
    @routes.route('/predict', methods=['POST'])
    def predict_route():
        data = request.get_json()
        prediction = predict(data)
        return jsonify(prediction)
