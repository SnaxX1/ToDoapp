from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "auth-service"})

@app.post("/login")
def login():
    return jsonify({"message": "login ok"})

@app.post("/register")
def register():
    return jsonify({"message": "user created"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
