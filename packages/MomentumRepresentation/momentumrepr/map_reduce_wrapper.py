#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


from rggraphenv import symbolic_functions
from rggraphutil import zeroDict
import copy
import graphine
import swiginac


class MapReduceAlgebraWrapper(object):
    def __init__(self, graph_to_coefficient):
        if not isinstance(graph_to_coefficient, dict):
            d = zeroDict()
            d[graph_to_coefficient] = symbolic_functions.CLN_ONE
            graph_to_coefficient = d
        self._graph_to_coefficient = graph_to_coefficient

    def apply(self, function_lambda):
        new_graph_to_coefficient = zeroDict()
        for g, c in self.x_items():
            obj = function_lambda(g)
            if isinstance(obj, (list, tuple)):
                for _g in obj:
                    new_graph_to_coefficient[_g] += symbolic_functions.CLN_ONE * c
            elif isinstance(obj, dict):
                for _g, _c in obj.items():
                    new_graph_to_coefficient[_g] += _c * c
            else:
                new_graph_to_coefficient[obj] += c * symbolic_functions.CLN_ONE
        return MapReduceAlgebraWrapper(new_graph_to_coefficient)

    def reduce(self, reduce_lambda, start_value, initial_transform_lambda=lambda a: a):
        return reduce(reduce_lambda, map(initial_transform_lambda, self._graph_to_coefficient.items()), start_value)

    def map(self, map_lambda):
        return MapReduceAlgebraWrapper(dict(map(lambda (e, c): map_lambda(e), c, self.x_items())))

    def map_with_coefficients(self, map_lambda):
        return map(lambda (e, c): map_lambda(e, c), self.x_items())

    def x_items(self):
        return self._graph_to_coefficient.iteritems()

    def __str__(self):
        sb = "\n---\n"
        for (g, c) in self.x_items():
            sb += "c=%s, g=%s\n" % (c, g)
        sb += "---\n"
        return sb

    def __mul__(self, other):
        if isinstance(other, (int, float, swiginac.refcounted)):
            new_graph_to_coefficient = zeroDict()
            for g, c in self.x_items():
                new_graph_to_coefficient[g] = c * other
            return MapReduceAlgebraWrapper(new_graph_to_coefficient)
        raise AssertionError()

    def __add__(self, other):
        return self._add_or_sub(other, True)

    def __sub__(self, other):
        return self._add_or_sub(other, False)

    def _add_or_sub(self, other, is_add):
        assert isinstance(other, MapReduceAlgebraWrapper)
        new_graph_to_coefficient = copy.copy(self._graph_to_coefficient)
        for g, c in other.x_items():
            new_graph_to_coefficient[g] += c if is_add else -c
        return MapReduceAlgebraWrapper(new_graph_to_coefficient)
