from flask import Flask, request, jsonify, render_template, send_file
import json, functools
import plotly as pl
import plotly.express as px
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

import api.lib.data as db

app = Flask(__name__)

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
    print(metrics)
    metric_labels = list(metrics[0].keys())
    metric_values = []
    for label in metric_labels:
        metric_values.append(functools.reduce(lambda a, b: a+b, [x[label] for x in metrics]) / len(metrics) * 2.5 + 2.5)
    print(metric_values)
    df = pd.DataFrame(dict(r=metric_values, theta=metric_labels))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself')
    # fig.show(config=dict(displayModeBar=False))
    score = functools.reduce(lambda a, b: a+b, metric_values) / len(metric_values)
    score = round(score, 2)
    return render_template('report.html', data=data, graph=json.dumps(fig, cls=pl.utils.PlotlyJSONEncoder), score=score)

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
