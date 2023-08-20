import requests, json, time, os

baseurl = "https://us-east-1.aws.data.mongodb-api.com/app/data-qozeq/endpoint/data/v1/action"
headers = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers': '*',
    'api-key': os.environ.get('MONGODB_API_KEY'), 
}

SL_DATASOURCE = "SemanticAttendantServerlessInstance"
SL_DATABASE = "SemanticLabsAttendant"

def prep_getone(collection, filter={}):
    return json.dumps({
        "collection": collection,
        "database": SL_DATABASE,
        "dataSource": SL_DATASOURCE,
        "filter": filter,
    })

def prep_query(collection, filter={}, projection={}, sort={}, limit=1000, skip=0):
    return json.dumps({
        "collection": collection,
        "database": SL_DATABASE,
        "dataSource": SL_DATASOURCE,
        "filter": filter,
        "projection": projection,
        "sort": sort,
        "limit": limit,
        "skip": skip
    })

def prep_insert(collection, document):
    ts_ms = int(time.time() * 1000)
    document["time"] = { "$date": { "$numberLong":  str(ts_ms)} }
    return json.dumps({
        "collection": collection,
        "database": SL_DATABASE,
        "dataSource": SL_DATASOURCE,
        "document": document
    })

def prep_update(collection, filter, update):
    return json.dumps({
        "collection": collection,
        "database": SL_DATABASE,
        "dataSource": SL_DATASOURCE,
        "filter": filter,
        "update": update
    })

def prep_delete(collection, filter):
    return json.dumps({
        "collection": collection,
        "database": SL_DATABASE,
        "dataSource": SL_DATASOURCE,
        "filter": filter
    })

def get_pull_request(session_id):
    url = f'{baseurl}/findOne'
    payload = prep_getone("amicus_pull_requests",
        filter={"session_id": session_id},
    )
    response = requests.request("POST", url, headers=headers, data=payload).json()
    return handle_findone_response(response)

def get_pull_request_files(session_id):
    url = f'{baseurl}/find'
    payload = prep_query("amicus_pull_request_files",
        filter={"session_id": session_id},
    )
    response = requests.request("POST", url, headers=headers, data=payload).json()
    return response['documents']

def add_pull_request(repo, pull_request):
    url = f'{baseurl}/insertOne'
    payload = prep_insert("amicus_pull_requests", {
        "session_id": repo["session_id"],
        "repo_name": repo["repo_name"],
        "repo_owner": repo["repo_owner"],
        "pull_request_id": pull_request["pull_request_id"],
        "latest_sha_commit": pull_request["latest_sha_commit"],
        "executive_summary": pull_request["executive_summary"],
        "long_summary": pull_request["long_summary"],
    })
    response = requests.request("POST", url, headers=headers, data=payload).json()
    return handle_insertone_response(response)

def add_pull_request_file(session_id, pull_request_file):
    url = f'{baseurl}/insertOne'
    payload = prep_insert("amicus_pull_request_files", {
        "session_id": session_id,
        "filename": pull_request_file["filename"],
        "code_summary": pull_request_file["results"]["code_summary"],
        "diff_json": pull_request_file["results"]["diff_json"],
        "metrics": pull_request_file["results"]["metrics"],
        "analysis_result": pull_request_file["results"]["analysis_result"],
    })
    response = requests.request("POST", url, headers=headers, data=payload).json()
    return handle_insertone_response(response)

def handle_findone_response(response):
    if 'document' in response:
        return response['document']
    return None

def handle_insertone_response(response):
    if 'insertedId' in response:
        return response['insertedId']
    return None

def handle_updateone_response(response):
    if 'modifiedCount' in response:
        return response['modifiedCount']
    return 0

def handle_deleteone_response(response):
    if 'deletedCount' in response:
        return response['deletedCount']
    return 0
