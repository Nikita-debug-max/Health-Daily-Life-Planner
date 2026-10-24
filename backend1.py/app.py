
import os

from flask import Flask, jsonify
from flask_cors import CORS
from health import health_bp
from auth import auth_bp
from tasks import tasks_bp
from meals import meals_bp
app = Flask(__name__)

# For local development only.
# Set SECRET_KEY to a strong, private environment variable
# before deploying the application.
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "dev-only-change-this-key-before-deployment"
)

CORS(app, supports_credentials=True)

# Register the authentication routes
app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(health_bp)
app.register_blueprint(meals_bp)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Health and Daily Life Planner Backend is running!"
    })


if __name__ == "__main__":
    app.run(debug=True)

