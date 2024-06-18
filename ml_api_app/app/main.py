from flask import Flask, request
from dotenv import load_dotenv
from app.routes import init_routes
from app.utils.logger import api_logger

load_dotenv()

app = Flask(__name__)
print("Initializing Flask app")
init_routes(app)
print("Routes initialized", app.url_map)


@app.before_request
def log_request_info():
    api_logger.info(
        f"Request: {request.method} {request.url} - Body: {request.get_json()}")


if __name__ == "__main__":
    print("Starting Flask app")
    app.run(debug=True)
