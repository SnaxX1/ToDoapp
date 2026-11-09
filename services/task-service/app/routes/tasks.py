from flask import Blueprint

from app.controllers.task_controller import TaskController


tasks_bp = Blueprint("tasks", __name__)
tasks_bp.add_url_rule("/", view_func=TaskController.get_all_tasks, methods=["GET"])
tasks_bp.add_url_rule("/", view_func=TaskController.create_task, methods=["POST"])
tasks_bp.add_url_rule("/<task_id>", view_func=TaskController.get_task, methods=["GET"])
tasks_bp.add_url_rule(
    "/<task_id>", view_func=TaskController.update_task, methods=["PUT"]
)
tasks_bp.add_url_rule(
    "/<task_id>", view_func=TaskController.delete_task, methods=["DELETE"]
)
