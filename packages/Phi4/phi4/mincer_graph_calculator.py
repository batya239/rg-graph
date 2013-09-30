#!/usr/bin/python
# -*- coding: utf8
import rggraphenv
import mincer


class MincerGraphCalculator(rggraphenv.AbstractGraphCalculator):
    """
    wrapper for mincer for usage in storage
    """
    def is_applicable(self, graph):
        return mincer.is_applicable(graph)

    def get_label(self):
        return "mincer graph calculator"

    def calculate(self, graph):
        return mincer.calculate_graph(graph)

    def init(self):
        mincer.init_mincer()

    def dispose(self):
        mincer.dispose_mincer()