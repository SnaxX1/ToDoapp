import os
from datetime import datetime

from bson import ObjectId
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from pymongo import MongoClient

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
JWTManager(app)

mongo = MongoClient(os.environ["MONGO_URI"])
tasks = mongo.get_default_database().tasks


def format_task(task):
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task.get("description", ""),
        "priority": task.get("priority", "medium"),
        "status": task.get("status", "pending"),
        "dueDate": task.get("dueDate"),
        "createdAt": task["createdAt"].isoformat(),
        "updatedAt": task["updatedAt"].isoformat(),
    }


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "task-service"})


@app.route("/tasks/", methods=["GET", "POST"])
@jwt_required()
def task_collection():
    user_id = get_jwt_identity()
    if request.method == "GET":
        query = {"userId": user_id}
        if request.args.get("status"):
            query["status"] = request.args["status"]
        if request.args.get("priority"):
            query["priority"] = request.args["priority"]
        result = [format_task(task) for task in tasks.find(query).sort("createdAt", -1)]
        return jsonify(result)

    data = request.get_json(silent=True) or {}
    if not data.get("title"):
        return jsonify({"error": "Title is required"}), 400
    now = datetime.utcnow()
    task = {
        "userId": user_id,
        "title": data["title"],
        "description": data.get("description", ""),
        "priority": data.get("priority", "medium"),
        "status": data.get("status", "pending"),
        "dueDate": data.get("dueDate"),
        "createdAt": now,
        "updatedAt": now,
    }
    result = tasks.insert_one(task)
    task["_id"] = result.inserted_id
    return jsonify(format_task(task)), 201


@app.route("/tasks/<task_id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def task_item(task_id):
    try:
        object_id = ObjectId(task_id)
    except Exception:
        return jsonify({"error": "Task not found"}), 404

    query = {"_id": object_id, "userId": get_jwt_identity()}
    task = tasks.find_one(query)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    if request.method == "GET":
        return jsonify(format_task(task))
    if request.method == "DELETE":
        tasks.delete_one(query)
        return jsonify({"message": "Task deleted"})

    data = request.get_json(silent=True) or {}
    updates = {
        key: data[key]
        for key in ("title", "description", "priority", "status", "dueDate")
        if key in data
    }
    if not updates:
        return jsonify({"error": "No fields to update"}), 400
    updates["updatedAt"] = datetime.utcnow()
    tasks.update_one(query, {"$set": updates})
    return jsonify(format_task(tasks.find_one(query)))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
