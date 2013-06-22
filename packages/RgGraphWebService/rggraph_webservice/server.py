#!/usr/bin/python
# -*- coding: utf8

__author__ = 'daddy-bear'

from flask import Flask, abort, make_response
import draw_graph_state

app = Flask(__name__)


@app.route("/")
def index():
    return "RG Graph Home Page"


@app.route("/graph-state/get-png/<rawGraphState>", methods=["GET"])
def getPngFromGraphState(rawGraphState=None):
    if rawGraphState is None:
        abort(400)
    else:
        png = draw_graph_state.generatePngStream(rawGraphState)
        response = make_response(png)
        response.headers['Content-Type'] = 'image/png'
        return response


if __name__ == "__main__":
    app.run()
