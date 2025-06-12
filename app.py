from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

SLACK_TOKEN = os.getenv("SLACK_TOKEN")

@app.route("/slack-proxy/<path:endpoint>", methods=["GET", "POST"])
def slack_proxy(endpoint):
    print("Incoming headers:", dict(request.headers))
    slack_url = f"https://slack.com/api/{endpoint}"
    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}",
        "Content-Type": "application/json; charset=utf-8"
    }

    if request.method == "POST":
        response = requests.post(slack_url, headers=headers, json=request.json)
    else:
        response = requests.get(slack_url, headers=headers, params=request.args)

    return jsonify(response.json()), response.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)