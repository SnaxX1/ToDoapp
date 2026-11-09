from flask import Blueprint

from app.controllers.user_controller import UserController


users_bp = Blueprint("users", __name__)
users_bp.add_url_rule("/register", view_func=UserController.register, methods=["POST"])
users_bp.add_url_rule("/login", view_func=UserController.login, methods=["POST"])
users_bp.add_url_rule("/profile", view_func=UserController.get_profile, methods=["GET"])
users_bp.add_url_rule("/refresh", view_func=UserController.refresh, methods=["POST"])
