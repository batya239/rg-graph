#!/usr/bin/python
# -*- coding: utf8
import graph_storage

__author__ = 'daddy-bear'


class AbstractGraphCalculator(object):
    def init(self):
        pass

    def dispose(self):
        pass

    def getLabel(self):
        raise NotImplementedError

    def calculate(self, graph):
        raise NotImplementedError

    def isApplicable(self, graph):
        raise NotImplementedError

_calculators = list()


def addCalculator(graphCalculator):
    graphCalculator.init()
    _calculators.append(graphCalculator)


def tryCalculate(graph, putValueToStorage=False):
    for c in _calculators:
        if c.isApplicable(graph):
            res = c.calculate(graph)
            if res is not None:
                if putValueToStorage:
                    graph_storage.put(graph, res)
                return res, c.getLabel()
    return None


def dispose():
    while len(_calculators) != 0:
        _calculators.pop().dispose()