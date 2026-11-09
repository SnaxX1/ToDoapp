from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.task_service import TaskService


class TaskController:
    @staticmethod
    @jwt_required()
    def get_all_tasks():
        result, status = TaskService.get_all_tasks(
            get_jwt_identity(),
            status=request.args.get("status"),
            priority=request.args.get("priority"),
        )
        return jsonify(result), status

    @staticmethod
    @jwt_required()
    def create_task():
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"error": "A JSON object is required"}), 400
        result, status = TaskService.create_task(get_jwt_identity(), data)
        return jsonify(result), status

    @staticmethod
    @jwt_required()
    def get_task(task_id):
        result, status = TaskService.get_task(task_id, get_jwt_identity())
        return jsonify(result), status

    @staticmethod
    @jwt_required()
    def update_task(task_id):
        data = request.get_json(silent=True) or {}
        result, status = TaskService.update_task(task_id, get_jwt_identity(), data)
        return jsonify(result), status

    @staticmethod
    @jwt_required()
    def delete_task(task_id):
        result, status = TaskService.delete_task(task_id, get_jwt_identity())
        return jsonify(result), status
