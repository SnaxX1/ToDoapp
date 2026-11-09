from datetime import datetime, timedelta

from flask_jwt_extended import create_access_token, create_refresh_token
from pymongo.errors import DuplicateKeyError

from app.models.user import User


class AuthService:
    @staticmethod
    def _user_response(user):
        created_at = user.get("createdAt")
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()
        return {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "createdAt": created_at,
        }

    @staticmethod
    def _token_response(user):
        identity = str(user["_id"])
        return {
            "user": AuthService._user_response(user),
            "access_token": create_access_token(
                identity=identity, expires_delta=timedelta(hours=1)
            ),
            "refresh_token": create_refresh_token(identity=identity),
        }

    @staticmethod
    def register_user(name, email, password):
        if not name or not email or not password:
            return {"error": "Name, email and password are required"}, 400
        if not isinstance(password, str) or len(password) < 6:
            return {"error": "Password must be at least 6 characters long"}, 400
        if not isinstance(email, str) or "@" not in email or "." not in email:
            return {"error": "Invalid email"}, 400

        try:
            user = User.create_user(name, email, password)
        except DuplicateKeyError:
            return {"error": "Email is already registered"}, 409

        response = AuthService._token_response(user)
        response["message"] = "User created"
        return response, 201

    @staticmethod
    def login_user(email, password):
        if not isinstance(email, str) or not email or not isinstance(password, str) or not password:
            return {"error": "Email and password are required"}, 400

        user = User.find_by_email(email)
        if not user or not User.verify_password(user, password):
            return {"error": "Invalid email or password"}, 401

        response = AuthService._token_response(user)
        response["message"] = "Login successful"
        return response, 200

    @staticmethod
    def refresh_token(identity):
        return {
            "access_token": create_access_token(
                identity=identity, expires_delta=timedelta(hours=1)
            )
        }, 200
