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
    storageFile = open(_STORAGE_FILE_NAME, "a")
    storageFile.write("\n")
    storageFile.write(str((graphStateAsString, value[0], value[1])))
    storageFile.close()


def get(graphState):
    return STORAGE.get(graphState)


def has(graphState):
    return STORAGE.has(graphState)


_STORAGE_FILE_NAME = "graph_storage.txt"

def _initStorage():
    if path.exists(_STORAGE_FILE_NAME):
        for line in open(_STORAGE_FILE_NAME, "r"):
            k, v1, v2 = eval(line)
            STORAGE.underlying[k] = (v1, v2)
    else:
        localStorageFile = open(_STORAGE_FILE_NAME, "a")
        for line in open(path.join(path.dirname(path.realpath(__file__)), _STORAGE_FILE_NAME), "r"):
            if not len(line):
                continue
            k, v1, v2 = eval(line)
            STORAGE.underlying[k] = (v1, v2)
            localStorageFile.write(str((k, v1, v2)))
            localStorageFile.write("\n")
        localStorageFile.close()


STORAGE = GraphStorage()
_initStorage()