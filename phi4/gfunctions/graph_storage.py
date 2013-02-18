#!/usr/bin/python
# -*- coding: utf8


class GraphStorage(object):
    def __init__(self):
        self.underlying = dict()

    def get(self, graphState):
        return self.underlying.get(str(graphState), None)

    def has(self, graphState):
        return str(graphState) in self.underlying


STORAGE = GraphStorage()
STORAGE.underlying["e11-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(0, 0)']"] = ("G(1, 1)", (1, -1))
STORAGE.underlying["e11-e-::['(0, 0)', '(1, 0)', '(2, -1)', '(0, 0)']"] = ("G(1, 2-lambda)", (2, -2))


def get(graphState):
    return STORAGE.get(graphState)


def has(graphState):
    return STORAGE.has(graphState)
