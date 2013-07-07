#!/usr/bin/python
# -*- coding: utf8
import gfunctions
import mincer


class MincerGraphCalculator(gfunctions.graph_calculator.AbstractGraphCalculator):
    def isApplicable(self, graph):
        mincer.isApplicable(graph)

    def getLabel(self):
        return "mincer graph calculator"

    def calculate(self, graph):
        return mincer.calculateGraph(graph)

    def init(self):
        mincer.initMincer()

    def dispose(self):
        mincer.disposeMincer()