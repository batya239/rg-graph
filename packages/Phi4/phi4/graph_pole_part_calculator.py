#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import graphine
import r
import common
import inject
import configure
from rggraphenv import symbolic_functions, abstract_graph_calculator


DEBUG = False


def calculate_graph_pole_part(graph):
    """
    can be used only for \phi4

    calculates some inversion of KR*
    """
    if DEBUG:
        print "calculate graph via pole part: %s, loops count: %s" % (graph, graph.getLoopsCount())
    try:
        r_operation = r.ROperation()
        assert graph.externalEdgesCount() == 2
        tadpole = graph.deleteEdges(graph.externalEdges())
        tails_count = 0
        for v in tadpole.vertices():
            d = 4 - len(tadpole.edges(v))
            if d < 0:
                return None
            tails_count += d
        if tails_count != 4:

            return None

        kr_star = r_operation.kr_star(tadpole)
        co_part = r_operation.kr_star(graph, minus_graph=True)
        return common.MSKOperation().calculate(kr_star - co_part + symbolic_functions.Order(1))
    except common.CannotBeCalculatedError:
        return None


class GraphPolePartCalculator(abstract_graph_calculator.AbstractGraphCalculator):
    def get_label(self):
        return "graph pole part calculator"

    def is_applicable(self, graph):
        if graph.getLoopsCount() != 5:
            return False
        for e in graph.allEdges():
            if e.weight != 1:
                return False
        return True

    def init(self):
        pass

    def calculate(self, graph):
        return calculate_graph_pole_part(graph)

    def dispose(self):
        pass