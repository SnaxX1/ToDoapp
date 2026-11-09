import os

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
JWTManager(app)

from app.routes.users import users_bp

app.register_blueprint(users_bp)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "auth-service"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
