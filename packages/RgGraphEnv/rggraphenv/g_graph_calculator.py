# !/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import swiginac

import abstract_graph_calculator
import symbolic_functions


G, G1, G2 = symbolic_functions.G, symbolic_functions.G1, symbolic_functions.G2


class GLoopCalculator(abstract_graph_calculator.AbstractGraphCalculator):
    def __init__(self, dimension):
        self._dimension = dimension
        self._lambda = dimension / symbolic_functions.CLN_TWO - symbolic_functions.CLN_ONE

    def get_label(self):
        return "loop calculator for dim = %s" % self._dimension

    def init(self):
        pass

    def dispose(self):
        pass

    def is_applicable(self, graph):
        return str(graph).startswith("e11|e|:")

    def calculate(self, graph):
        graph_state_str = str(graph)
        vertices = list(graph.vertices - set([graph.external_vertex]))
        edges = filter(lambda e: graph.external_vertex not in e.nodes, graph.edges(vertices[0]))

        alpha = edges[0].weight
        beta = edges[1].weight

        not_empty = filter(lambda e: e.arrow is not None and not e.arrow.is_null(), edges)

        if not_empty is not None and len(not_empty):
            not_empty_numerator_edge = not_empty[0]
            copy = list(edges)
            copy.remove(not_empty_numerator_edge)
            other_edge = copy[0]
            if other_edge.arrow.is_null():
                sign = 1 if not_empty_numerator_edge.arrow.is_left() else -1
                if not_empty_numerator_edge != edges[0]:
                    t = alpha
                    alpha = beta
                    beta = t
                return sign * symbolic_functions.G1(alpha.subs(self._lambda), beta.subs(self._lambda),
                                                    d=self._dimension), alpha + beta - (1, 1)
            else:
                sign = 1 if not_empty_numerator_edge.arrow == other_edge.arrow else -1
                return sign * symbolic_functions.G2(alpha.subs(self._lambda), beta.subs(self._lambda),
                                                    d=self._dimension), alpha + beta - (2, 1)
        return G(alpha.subs(self._lambda), beta.subs(self._lambda), d=self._dimension), alpha + beta - (1, 1)