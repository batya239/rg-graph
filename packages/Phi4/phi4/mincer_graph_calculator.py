#!/usr/bin/python
# -*- coding: utf8
import rggraphenv
import mincer


class MincerGraphCalculator(rggraphenv.AbstractGraphCalculator):
    def isApplicable(self, graph):
        return mincer.isApplicable(graph)

    def getLabel(self):
        return "mincer graph calculator"

    def calculate(self, graph):
        return mincer.calculateGraph(graph)

    def init(self):
        mincer.initMincer()

    def dispose(self):
        mincer.disposeMincer()