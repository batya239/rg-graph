#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


from rggraphenv import symbolic_functions
from rggraphutil import zeroDict
import copy
import graphine
import swiginac


class MapReduceAlgebraWrapper(object):
    def __init__(self, mappings):
        if not isinstance(mappings, dict):
            d = zeroDict()
            d[mappings] = symbolic_functions.CLN_ONE
            mappings = d
        self._mappings = mappings

    def apply(self, function_lambda):
        new_mappings = zeroDict()
        for g, c in self.x_items():
            obj = function_lambda(g)
            if isinstance(obj, (list, tuple)):
                for _g in obj:
                    new_mappings[_g] += symbolic_functions.CLN_ONE * c
            elif isinstance(obj, dict):
                for _g, _c in obj.items():
                    new_mappings[_g] += _c * c
            else:
                new_mappings[obj] += c * symbolic_functions.CLN_ONE
        return MapReduceAlgebraWrapper(new_mappings)

    def reduce(self, reduce_lambda, start_value, initial_transform_lambda=lambda a: a):
        return reduce(reduce_lambda, map(initial_transform_lambda, self._mappings.items()), start_value)

    def map(self, map_lambda):
        return MapReduceAlgebraWrapper(dict(map(lambda (e, c): map_lambda(e), c, self.x_items())))

    def map_with_coefficients(self, map_lambda):
        return map(lambda (e, c): map_lambda(e, c), self.x_items())

    def x_items(self):
        return self._mappings.iteritems()

    def __str__(self):
        sb = "\n---\n"
        for (g, c) in self.x_items():
            sb += "c=%s, g=%s\n" % (c, g)
        sb += "---\n"
        return sb

    def __mul__(self, other):
        if isinstance(other, (int, float, swiginac.refcounted)):
            new_mappings = zeroDict()
            for g, c in self.x_items():
                new_mappings[g] = c * other
            return MapReduceAlgebraWrapper(new_mappings)
        raise AssertionError()

    def __add__(self, other):
        return self._add_or_sub(other, True)

    def __sub__(self, other):
        return self._add_or_sub(other, False)

    def _add_or_sub(self, other, is_add):
        assert isinstance(other, MapReduceAlgebraWrapper)
        new_mappings = copy.copy(self._mappings)
        for g, c in other.x_items():
            new_mappings[g] += c if is_add else -c
        return MapReduceAlgebraWrapper(new_mappings)
