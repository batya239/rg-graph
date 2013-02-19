#!/usr/bin/python
# -*- coding: utf8
from os import path
import graph_state


class GraphStorage(object):
    def __init__(self):
        self.underlying = dict()

    def get(self, graphState):
        return self.underlying.get(str(graphState), None)

    def has(self, graphState):
        return str(graphState) in self.underlying


def put(graphState, value):
    assert isinstance(graphState, graph_state.GraphState)
    assert len(value) == 2
    assert isinstance(value[0], str)
    assert isinstance(value[1], tuple)
    assert len(value[1]) == 2
    if has(graphState):
        return
    graphStateAsString = str(graphState)
    STORAGE.underlying[graphStateAsString] = value
    storageFile = open(_getStoragePath(), "a")
    storageFile.write("\n")
    storageFile.write(str((graphStateAsString, value[0], value[1])))
    storageFile.close()


def get(graphState):
    return STORAGE.get(graphState)


def has(graphState):
    return STORAGE.has(graphState)


def _getStoragePath():
    return path.join(path.dirname(path.realpath(__file__)), "graph_storage.txt")


def _initStorage():
    for line in open(_getStoragePath(), "r"):
        k, v1, v2 = eval(line)
        STORAGE.underlying[k] = (v1, v2)

STORAGE = GraphStorage()
_initStorage()