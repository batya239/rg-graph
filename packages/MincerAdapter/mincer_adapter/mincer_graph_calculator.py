#!/usr/bin/python
# -*- coding: utf8
import gfunctions
import mincer


class MincerGraphCalculator(gfunctions.graph_calculator.AbstractGraphCalculator):
    def __init__(self, dimensionModel):
        self._dimensionModel = dimensionModel

    def isApplicable(self, graph):
        return mincer.isApplicable(graph)

    def getLabel(self):
        return "mincer graph calculator"

    def calculate(self, graph):
        return mincer.calculateGraph(graph, self._dimensionModel)

    def init(self):
        mincer.initMincer()

    def dispose(self):
        mincer.disposeMincer()