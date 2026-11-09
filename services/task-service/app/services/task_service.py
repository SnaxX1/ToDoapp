from datetime import datetime

from app.models.task import Task


VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"pending", "in progress", "done"}


class TaskService:
    @staticmethod
    def format_task(task):
        def format_date(value):
            if isinstance(value, datetime):
                return value.isoformat()
            return value

        return {
            "id": str(task["_id"]),
            "title": task["title"],
            "description": task.get("description", ""),
            "priority": task.get("priority", "medium"),
            "status": task.get("status", "pending"),
            "dueDate": format_date(task.get("dueDate")),
            "createdAt": format_date(task.get("createdAt")),
            "updatedAt": format_date(task.get("updatedAt")),
        }

    @staticmethod
    def create_task(user_id, data):
        if not data.get("title"):
            return {"error": "Title is required"}, 400
        priority = data.get("priority", "medium")
        status = data.get("status", "pending")
        if not isinstance(priority, str) or priority not in VALID_PRIORITIES:
            return {"error": "Invalid priority"}, 400
        if not isinstance(status, str) or status not in VALID_STATUSES:
            return {"error": "Invalid status"}, 400
        return TaskService.format_task(Task.create_task(user_id, data)), 201

    @staticmethod
    def get_all_tasks(user_id, status=None, priority=None):
        result = Task.get_user_tasks(user_id, status, priority)
        return [TaskService.format_task(task) for task in result], 200

    @staticmethod
    def get_task(task_id, user_id):
        task = Task.get_task_by_id(task_id, user_id)
        if not task:
            return {"error": "Task not found"}, 404
        return TaskService.format_task(task), 200

    @staticmethod
    def update_task(task_id, user_id, data):
        task = Task.get_task_by_id(task_id, user_id)
        if not task:
            return {"error": "Task not found"}, 404
        if not isinstance(data, dict):
            return {"error": "A JSON object is required"}, 400

        updates = {
            key: data[key]
            for key in ("title", "description", "priority", "status", "dueDate")
            if key in data
        }
        if not updates:
            return {"error": "No fields to update"}, 400
        if "priority" in updates and (
            not isinstance(updates["priority"], str)
            or updates["priority"] not in VALID_PRIORITIES
        ):
            return {"error": "Invalid priority"}, 400
        if "status" in updates and (
            not isinstance(updates["status"], str)
            or updates["status"] not in VALID_STATUSES
        ):
            return {"error": "Invalid status"}, 400

        updated = Task.update_task(task_id, user_id, updates)
        if not updated:
            return {"error": "Task not found"}, 404
        return TaskService.format_task(updated), 200

    @staticmethod
    def delete_task(task_id, user_id):
        if not Task.delete_task(task_id, user_id):
            return {"error": "Task not found"}, 404
        return {"message": "Task deleted"}, 200
