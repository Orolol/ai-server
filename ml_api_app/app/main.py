from flask import Flask, request
from dotenv import load_dotenv
from app.routes import init_routes
from app.utils.logger import api_logger

load_dotenv()

app = Flask(__name__)
print("Initializing Flask app")
print("Initializing routes")
init_routes(app)
print("Routes initialized", app.url_map)
print("Routes initialized", app.url_map)


@app.before_request
def log_request_info():
    print(f"Logging request: {request.method} {request.url}")
    print(f"Request headers: {request.headers}")
    print(f"Request body: {request.get_data(as_text=True)}")
    api_logger.info(
        f"Request: {request.method} {request.url} - Headers: {request.headers} - Body: {request.get_data(as_text=True)}")


if __name__ == "__main__":
    print("Starting Flask app")
    print("Starting Flask app")
    app.run(debug=True)
