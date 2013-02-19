#!/usr/bin/python
# -*- coding: utf8
from os import path


class GraphStorage(object):
    def __init__(self):
        self.underlying = dict()

    def get(self, graphState):
        return self.underlying.get(str(graphState), None)

    def has(self, graphState):
        return str(graphState) in self.underlying


def get(graphState):
    return STORAGE.get(graphState)


def has(graphState):
    return STORAGE.has(graphState)


def _initStorage():
    for line in open(path.join(path.dirname(path.realpath(__file__)), "graph_storage.txt"), "r"):
        k, v1, v2 = eval(line)
        STORAGE.underlying[k] = (v1, v2)

STORAGE = GraphStorage()
_initStorage()
