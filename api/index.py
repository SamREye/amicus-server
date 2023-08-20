from flask import Flask, request, jsonify, render_template, send_file
import json, functools
from flask_cors import CORS

from dotenv import load_dotenv
load_dotenv()

import api.lib.data as db

app = Flask(__name__)
CORS(app)

# Route for favicon
@app.route('/favicon.ico')
def favicon():
    return send_file('favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def home():
    return 'Home Page'

@app.route('/pr/report/show/<session_id>', methods=["GET"])
def show_report(session_id):
    data = db.get_pull_request(session_id)
    data["files"] = db.get_pull_request_files(session_id)
    metrics = [json.loads(x["metrics"]) for x in data["files"]]
    metric_labels = list(metrics[0].keys())
    metric_values = []
    for label in metric_labels:
        value = functools.reduce(lambda a, b: a+b, [x[label] for x in metrics]) / len(metrics) * 2.5 + 2.5
        value = round(value, 2)
        metric_values.append(value)
    score = functools.reduce(lambda a, b: a+b, metric_values) / len(metric_values)
    score = round(score, 2)
    metric_labels = [x[0].upper() + x[1:] for x in metric_labels]
    consolidated_metrics = dict(zip(metric_labels, metric_values))
    return render_template('report.html', data=data, metrics=consolidated_metrics, score=score)

@app.route('/pr/report/get/<session_id>', methods=["GET"])
def get_report(session_id):
    data = db.get_pull_request(session_id)
    data["results"] = db.get_pull_request_files(session_id)
    return jsonify(data)

@app.route('/pr/report/comment/<session_id>', methods=["GET"])
def get_comment(session_id):
    data = db.get_pull_request(session_id)
    data["results"] = db.get_pull_request_files(session_id)
    comment = data["executive_summary"]
    comment += "\n\nCheck out the [Amicus Brief](https://amicus.semantic-labs.com/pr/report/show/" + session_id + ")."
    return jsonify({"comment": comment})

@app.route('/pr/report/markdown/<session_id>', methods=["GET"])
def get_document_chunks(session_id):
    document = "# Amicus Brief\n\n"
    data = db.get_pull_request(session_id)
    for field in ["repo_name", "repo_owner", "pull_request_id", "latest_sha_commit", "executive_summary", "long_summary"]:
        if field in data:
            document += "## " + field.replace("_", " ") + "\n\n"
            document += str(data[field]) + "\n\n"
    data["results"] = db.get_pull_request_files(session_id)
    document += "# Files\n\n"
    for file in data["results"]:
        document += "## " + file["filename"] + "\n\n"
        for field in ["code_summary", "diff_json", "analysis_result", "metrics"]:
            if field in file:
                if field == "metrics":
                    document += "### Metrics\n\n"
                    metrics = json.loads(file[field])
                    for metric in metrics:
                        document += "* " + metric + ": " + str(metrics[metric]) + "\n"
                else:
                    document += "### " + field.replace("_", " ") + "\n\n"
                    document += file[field] + "\n\n"
    print(document)
    return jsonify({"document": document})

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
