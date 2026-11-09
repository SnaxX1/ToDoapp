from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import DESCENDING

from app.extensions import tasks


class Task:
    @staticmethod
    def create_task(user_id, data):
        now = datetime.utcnow()
        task = {
            "userId": str(user_id),
            "title": data["title"],
            "description": data.get("description", ""),
            "priority": data.get("priority", "medium"),
            "status": data.get("status", "pending"),
            "dueDate": data.get("dueDate"),
            "createdAt": now,
            "updatedAt": now,
        }
        task["dueDate"] = Task.parse_due_date(task["dueDate"])
        result = tasks.insert_one(task)
        task["_id"] = result.inserted_id
        return task

    @staticmethod
    def parse_due_date(value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return value
        return value

    @staticmethod
    def _query_for_id(task_id, user_id):
        try:
            return {"_id": ObjectId(task_id), "userId": str(user_id)}
        except (InvalidId, TypeError):
            return None

    @staticmethod
    def get_user_tasks(user_id, status=None, priority=None):
        query = {"userId": str(user_id)}
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        return list(tasks.find(query).sort("createdAt", DESCENDING))

    @staticmethod
    def get_task_by_id(task_id, user_id):
        query = Task._query_for_id(task_id, user_id)
        return tasks.find_one(query) if query else None

    @staticmethod
    def update_task(task_id, user_id, updates):
        query = Task._query_for_id(task_id, user_id)
        if not query:
            return None
        updates = dict(updates)
        if "dueDate" in updates:
            updates["dueDate"] = Task.parse_due_date(updates["dueDate"])
        updates["updatedAt"] = datetime.utcnow()
        tasks.update_one(query, {"$set": updates})
        return tasks.find_one(query)

    @staticmethod
    def delete_task(task_id, user_id):
        query = Task._query_for_id(task_id, user_id)
        return bool(query and tasks.delete_one(query).deleted_count)
