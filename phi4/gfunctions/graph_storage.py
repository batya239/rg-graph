#!/usr/bin/python
# -*- coding: utf8

IN_MEMORY_GRAPH_STORAGE_INSTANCE = None


def getDefaultStorage(obj=IN_MEMORY_GRAPH_STORAGE_INSTANCE):
    if obj is not IN_MEMORY_GRAPH_STORAGE_INSTANCE:
        raise RuntimeError, "you should no pass parameters to this function"
    if obj is None:
        obj = InMemoryGraphStorage()
        obj._read()
    return obj


class GraphStorage(object):
    def get(self, graphState):
        pass

    def has(self, graphState):
        pass

    def put(self, graphState, value):
        pass


class InMemoryGraphStorage(GraphStorage):
    def __init__(self):
        self.underlying = dict()

    def get(self, graphState):
        self.underlying.get(str(graphState), None)

    def has(self, graphState):
        self.underlying.has_key(graphState)

    def put(self, graphState, value):
        raise NotImplementedError

    def _read(self):
        fill(self.underlying)


def fill(storageDict):
    pass

