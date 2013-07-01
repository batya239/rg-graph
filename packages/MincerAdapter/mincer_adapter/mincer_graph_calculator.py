#!/usr/bin/python
# -*- coding: utf8
import gfunctions
import mincer


class MincerGraphCalculator(gfunctions.graph_calculator.AbstractGraphCalculator):
    def isApplicable(self, graph):
        if graph.calculateLoopsCount() > 3:
            return False
        for e in graph.allEdges():
            c = e.colors
            if c is None or len(c) != 2:
                return False
            return c[1] == 0 and c[0] == int(c[0])

    def getLabel(self):
        return "mincer graph calculator"

    def calculate(self, graph):
        return mincer.calculateGraph(graph)

    def init(self):
        mincer.initMincer()

    def dispose(self):
        mincer.disposeMincer()