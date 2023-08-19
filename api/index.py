from flask import Flask, request, jsonify
from dotenv import load_dotenv
load_dotenv()

import api.lib.data as db

app = Flask(__name__)

@app.route('/')
def home():
    return 'Home Page'

@app.route('/pr/report/show/<session_id>', methods=["GET"])
def show_report(session_id):
    data = db.get_pull_request(session_id)
    data["results"] = db.get_pull_request_files(session_id)
    return 'Home Page'

@app.route('/pr/report/get/<session_id>', methods=["GET"])
def get_report(session_id):
    data = db.get_pull_request(session_id)
    data["results"] = db.get_pull_request_files(session_id)
    return jsonify(data)

@app.route('/pr/report/add', methods=["POST"])
def post_report():
    # Get report from payload
    report = request.json.get("review")
    # Add report to database
    result = db.add_pull_request(report)
    # Add pull request files to database
    for file in report["results"]:
        result = db.add_pull_request_file(report["session_id"], file)
    return jsonify({"status": "success"})
