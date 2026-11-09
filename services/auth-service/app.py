import os
from datetime import datetime, timedelta

from bson import ObjectId
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
JWTManager(app)

mongo = MongoClient(os.environ["MONGO_URI"])
users = mongo.get_default_database().users
users.create_index("email", unique=True)


def user_response(user):
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "createdAt": user["createdAt"].isoformat(),
    }


def token_response(user):
    identity = str(user["_id"])
    return {
        "user": user_response(user),
        "access_token": create_access_token(identity=identity),
        "refresh_token": create_refresh_token(identity=identity),
    }


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "auth-service"})


@app.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required"}), 400

    user = {
        "name": name,
        "email": email,
        "password": generate_password_hash(password),
        "createdAt": datetime.utcnow(),
    }
    try:
        result = users.insert_one(user)
    except DuplicateKeyError:
        return jsonify({"error": "Email is already registered"}), 409

    user["_id"] = result.inserted_id
    response = token_response(user)
    response["message"] = "User created"
    return jsonify(response), 201


@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    user = users.find_one({"email": data.get("email")})
    if not user or not check_password_hash(user["password"], data.get("password", "")):
        return jsonify({"error": "Invalid email or password"}), 401

    response = token_response(user)
    response["message"] = "Login successful"
    return jsonify(response)


@app.get("/profile")
@jwt_required()
def profile():
    user = users.find_one({"_id": ObjectId(get_jwt_identity())})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_response(user))


@app.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    return jsonify(
        {"access_token": create_access_token(identity=get_jwt_identity())}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
