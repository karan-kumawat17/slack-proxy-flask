# Importing necessary libraries
from flask import Flask, request, jsonify
import requests
import os
import logging
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

"""Creating the flask app with CORS policy"""
app = Flask(__name__)
CORS(app)

"""Setting the log level"""
logging.basicConfig(
    level=logging.INFO
)

SLACK_API_BASE = "https://slack.com/api"
SLACK_TOKEN = os.getenv("SLACK_TOKEN")

if not SLACK_TOKEN:
    raise EnvironmentError("SLACK_TOKEN not set in environment variables.")

HEADERS = {
    "Authorization": f"Bearer {SLACK_TOKEN}",
    "Content-Type": "application/json; charset=utf-8"
}

@app.route("/slack-proxy/<path:endpoint>", methods=["GET", "POST"])
def slack_proxy(endpoint):
    print("Incoming headers:", dict(request.headers))

    slack_url = f"{SLACK_API_BASE}/{endpoint}"

    try:
        if request.method == "GET":
            response = requests.get(slack_url, headers=HEADERS, params=request.args)
        elif request.method == "POST":
            if request.is_json:
                payload = request.get_json()
            else:
                return jsonify({"error": "Expected JSON body"}), 400
            
            response = requests.post(slack_url, headers=HEADERS, json=payload)
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"Slack request failed: {e}")
        return jsonify({"error": "Slack API request failed"}), 500
    except Exception as e:
        logging.exception("Unexpected error")
        return jsonify({"error": "Unexpected server error"}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    return jsonify({
        "error": e.name,
        "description": e.description,
        "code": e.code
    }), e.code

@app.errorhandler(Exception)
def handle_generic_exception(e):
    logging.exception("Unhandled exception")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)