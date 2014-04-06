#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import graphine
import r
import common
import inject
import configure
from rggraphenv import symbolic_functions, abstract_graph_calculator
from rggraphutil import VariableAwareNumber


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
        return common.MSKOperation().calculate(kr_star - co_part + symbolic_functions.Order(symbolic_functions.CLN_ONE))
    except common.CannotBeCalculatedError:
        return None


def get_lambda():
    return inject.instance("dimension") / symbolic_functions.cln(2) - symbolic_functions.CLN_ONE


def calculate_graph_p_factor(graph):
    factor0 = 0
    arrow_factor = 0
    for e in graph.internalEdges():
        arrow_factor += 1 if e.arrow is not None and not e.arrow.is_null() else 0
        factor0 += e.weight.a
    arrow_factor /= 2
    f = VariableAwareNumber("l", factor0 - graph.getLoopsCount() - arrow_factor, - graph.getLoopsCount())
    return f


class GraphPolePartCalculator(abstract_graph_calculator.AbstractGraphCalculator):
    def get_label(self):
        return "graph pole part calculator for 5 loops"

    def is_applicable(self, graph):
        if graph.getLoopsCount() not in (5,):
            return False
        for e in graph.allEdges():
            if e.weight != 1:
                return False
        return True

    def init(self):
        pass

    def calculate(self, graph):
        eps_part = calculate_graph_pole_part(graph)
        if eps_part is None:
            return None
        p_factor = calculate_graph_p_factor(graph)
        return eps_part.subs(symbolic_functions.p == symbolic_functions.CLN_ONE), p_factor

    def dispose(self):
        pass