#!/usr/bin/python
# -*- coding: utf8

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


def tryCalculate(graph):
    for c in _calculators:
        if c.isApplicable(graph):
            res = c.calculate(graph)
            if res is not None:
                return res, c.getLabel()
    return None


def dispose():
    for c in _calculators:
        c.dispose()




