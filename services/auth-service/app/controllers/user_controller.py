from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models.user import User
from app.services.auth_service import AuthService


class UserController:
    @staticmethod
    def register():
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"error": "A JSON object is required"}), 400
        response, status = AuthService.register_user(
            data.get("name"), data.get("email"), data.get("password")
        )
        return jsonify(response), status

    @staticmethod
    def login():
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"error": "A JSON object is required"}), 400
        response, status = AuthService.login_user(
            data.get("email"), data.get("password")
        )
        return jsonify(response), status

    @staticmethod
    @jwt_required()
    def get_profile():
        user = User.find_by_id(get_jwt_identity())
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(AuthService._user_response(user))

    @staticmethod
    @jwt_required(refresh=True)
    def refresh():
        response, status = AuthService.refresh_token(get_jwt_identity())
        return jsonify(response), status
