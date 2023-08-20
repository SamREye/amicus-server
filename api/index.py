from flask import Flask, request, jsonify, render_template
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
    data["files"] = db.get_pull_request_files(session_id)
    file_list = [x["filename"] for x in data["files"]]
    # print(data)
    return render_template('report.html', data=data, file_list=file_list)

@app.route('/pr/report/get/<session_id>', methods=["GET"])
def get_report(session_id):
    data = db.get_pull_request(session_id)
    data["results"] = db.get_pull_request_files(session_id)
    return jsonify(data)

@app.route('/pr/report/add', methods=["POST"])
def post_report():
    # Get report from payload
    reports = request.json.get("reviews")
    # Add pull request files to database
    for repo in reports:
        # Add report to database
        for pr in repo["results"]:
            db.add_pull_request(repo, pr)
            for file in pr["data"]:
                result = db.add_pull_request_file(repo["session_id"], file)
    return jsonify({"status": "success"})
