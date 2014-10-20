#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import graphine
import common
import inject
import configure
import r
from rggraphenv import symbolic_functions, abstract_graph_calculator, log
from rggraphutil import VariableAwareNumber


DEBUG = False


def calculate_graph_pole_part(graph):
    """
    can be used only for \phi4

    calculates some inversion of KR*
    """
    if log.is_debug_enabled():
        log.debug("calculate graph via pole part: %s, loops count: %s" % (graph, graph.loops_count))
    try:
        r_operation = r.RStar()
        assert graph.external_edges_count == 2
        tadpole = graph - graph.external_edges
        tails_count = 0
        for v in tadpole.vertices:
            d = 4 - len(tadpole.edges(v))
            if d < 0:
                return None
            tails_count += d
        if tails_count != 4:
            return None

        kr_star = r_operation.kr_star(tadpole)
        co_part = r_operation.kr_star(graph, minus_graph=True)

        kr_star = kr_star.evaluate()
        co_part = co_part.evaluate()
        return common.MSKOperation().calculate(kr_star - co_part + symbolic_functions.Order(symbolic_functions.CLN_ONE))
    except common.CannotBeCalculatedError:
        return None


def calculate_graph_p_factor(graph):
    factor0 = 0
    arrow_factor = 0
    for e in graph.internal_edges:
        arrow_factor += 1 if e.arrow is not None and not e.arrow.is_null() else 0
        factor0 += e.weight.a
    arrow_factor /= 2
    f = VariableAwareNumber("l", factor0 - graph.loops_count - arrow_factor, - graph.loops_count)
    return f


class GraphPolePartCalculator(abstract_graph_calculator.AbstractGraphCalculator):
    def get_label(self):
        return "graph pole part calculator for 5 loops"

    def is_applicable(self, graph):
        if graph.loops_count not in (5,):
            return False
        for e in graph:
            if not e.is_external() and e.weight != 1:
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