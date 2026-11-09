import os

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
JWTManager(app)

from app.routes.tasks import tasks_bp

app.register_blueprint(tasks_bp, url_prefix="/tasks")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "task-service"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
