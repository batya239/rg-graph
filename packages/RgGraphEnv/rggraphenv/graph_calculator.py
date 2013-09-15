#!/usr/bin/python
# -*- coding: utf8
import storage

__author__ = 'daddy-bear'

_calculators = list()


def addCalculator(graphCalculator):
    graphCalculator.init()
    _calculators.append(graphCalculator)


def tryCalculate(graph, putValueToStorage=False):
    for c in _calculators:
        if c.isApplicable(graph):
            res = c.calculate(graph)
            if res is not None:
                if putValueToStorage and not storage.hasGraph(graph):
                    storage.putGraph(graph, res, c.getLabel())
                return res, c.getLabel()
    return None


def dispose():
    while len(_calculators) != 0:
        _calculators.pop().dispose()