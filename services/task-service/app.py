from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "task-service"})

@app.get("/tasks")
def list_tasks():
    return jsonify({"tasks": ["task-1", "task-2"]})

@app.post("/tasks")
def create_task():
    return jsonify({"message": "task created"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
