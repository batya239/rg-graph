#!/usr/bin/python
# -*- coding: utf8

__author__ = 'daddy-bear'

from flask import Flask, abort, make_response, render_template, send_from_directory
import draw_graph_state
import rggraphenv.storage

rggraphenv.storage.initStorage("phi4", None, False)

app = Flask(__name__)


@app.route("/")
def index():
    return "RG Graph Home Page"


@app.route("/graph-state/get-png/<raw_graph_state>", methods=["GET"])
def get_png_from_graph_state(raw_graph_state=None):
    if raw_graph_state is None:
        abort(400)
    else:
        png = draw_graph_state.generate_png_stream(raw_graph_state)
        response = make_response(png)
        response.headers['Content-Type'] = 'image/png'
        return response

@app.route("/graph-state/", methods=["GET"])
def get_graph_state():
    return render_template("graph-state.html", td_iterator=xrange(4))

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('templates/js', filename)

_KR1_NAME = "kr1"
_R1_NAME = "r1"
_R_NAME = "r"
_V_NAME = "value"


@app.route("/operation/<operation_name>/graph-state/<raw_graph_state>", methods=["GET"])
def get_operation_result_from_graph_state(operation_name=None, raw_graph_state=None):
    if operation_name is None or raw_graph_state is None:
        abort(400)
    else:
        return "page under construction"


if __name__ == "__main__":
    app.run()
