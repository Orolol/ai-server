from flask import Flask
from dotenv import load_dotenv
import os
from app.routes import init_routes

load_dotenv()

app = Flask(__name__)
init_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
