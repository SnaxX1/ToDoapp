import os

import requests
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5001")
TASK_SERVICE_URL = os.getenv("TASK_SERVICE_URL", "http://localhost:5002")
FORWARDED_METHODS = ["GET", "POST", "PUT", "DELETE"]


def forward_request(base_url, path):
    headers = {
        key: value
        for key, value in request.headers
        if key.lower() in ("authorization", "content-type")
    }

    try:
        upstream = requests.request(
            request.method,
            f"{base_url}/{path}",
            params=request.args,
            data=request.get_data(),
            headers=headers,
            timeout=5,
        )
    except requests.RequestException:
        return jsonify({"error": "Service unavailable"}), 502

    return Response(
        upstream.content,
        status=upstream.status_code,
        content_type=upstream.headers.get("Content-Type"),
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "gateway"})


@app.route("/api/users", defaults={"path": ""}, methods=FORWARDED_METHODS)
@app.route("/api/users/<path:path>", methods=FORWARDED_METHODS)
def auth(path):
    return forward_request(AUTH_SERVICE_URL, path)


@app.route("/api/tasks", defaults={"path": ""}, methods=FORWARDED_METHODS)
@app.route("/api/tasks/<path:path>", methods=FORWARDED_METHODS)
def tasks(path):
    return forward_request(TASK_SERVICE_URL, f"tasks/{path}".rstrip("/"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
