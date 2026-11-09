from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "gateway"})

@app.get("/auth")
def auth():
    return jsonify({"message": "redirect to auth-service"})

@app.get("/tasks")
def tasks():
    return jsonify({"message": "redirect to task-service"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
