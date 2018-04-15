# app.py

import os

from flask import Flask
from flask import request
from flask import jsonify

from route import FileRoute


app = Flask(__name__)
app.url_map.strict_slashes = False

DIRECTORY = os.path.join(os.path.dirname(__file__), "data")


def form_data_response(data, **kwargs):
    """
    Utility function for formulating responses with consistent attributes.
    Incidentally also solves the problem with jsons
    """
    kwargs.update({"data": data})
    return jsonify(kwargs)


def access_endpoint(endpoint):
    return FileRoute("{}/{}.json".format(DIRECTORY, endpoint))


@app.route("/")
def index():
    jsons = filter(lambda f: f.endswith(".json"), os.listdir(DIRECTORY))
    return form_data_response(jsons)


@app.route("/<endpoint>", methods=['GET', 'POST'])
def get_records(endpoint):
    END = access_endpoint(endpoint)
    if request.method == "GET":
        ret = END.index()
    if request.method == "POST":
        ret = END.post(request.json)
    return form_data_response(ret)


@app.route("/<endpoint>/<path:rec_id>", methods=['GET', 'POST'])
def get_id(endpoint, rec_id):
    END = access_endpoint(endpoint)
    if request.method == "GET":
        ret = END.get(rec_id)
    if request.method == "POST":
        ret = END.put(rec_id, request.json)
    return form_data_response(ret)
