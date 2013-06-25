#!/usr/bin/python
# -*- coding: utf8

__author__ = 'daddy-bear'

class AbstractGraphCalculator(object):
    def getLabel(self):
        raise NotImplementedError

    def calculate(self, graph):
        raise NotImplementedError

    def isApplicable(self, graph):
        raise NotImplementedError


class MincerGraphCalculator(AbstractGraphCalculator):
    def getLabel(self):
        return "mincer graph calculator"


_calculators = list()


def addCalculator(graphCalculator):
    if isinstance(graphCalculator, AbstractGraphCalculator):
        _calculators.append(graphCalculator)
    else:
        raise ValueError("unsupported calculator")

def tryCalculate(graph):
    for c in _calculators:
        if c.isApplicable(graph):
            res = c.calculate(graph)
            if res is not None:
                return res, c.getLabel()
    return None




