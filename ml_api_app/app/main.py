from flask import Flask, request
from dotenv import load_dotenv
import os
from app.routes import routes
from app.utils.logger import api_logger

load_dotenv()

app = Flask(__name__)
init_routes(app)

@app.before_request
def log_request_info():
    api_logger.info(f"Request: {request.method} {request.url} - Body: {request.get_json()}")

if __name__ == "__main__":
    app.run(debug=True)
