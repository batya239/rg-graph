#!/usr/bin/python
# -*- coding: utf8


class GraphStorage(object):
    def __init__(self):
        self.underlying = dict()

    def get(self, graphState):
        return self.underlying.get(str(graphState), None)

    def has(self, graphState):
        return self.underlying.has_key(str(graphState))

STORAGE = GraphStorage()
STORAGE.underlying["ee11-ee-::['None', 'None', '(1, 0)', '(1, 0)', 'None', 'None']"] = ("G(1, 1)", (2, -1))


def get(graphState):
    STORAGE.get(graphState)


def has(graphState):
    STORAGE.has(graphState)
