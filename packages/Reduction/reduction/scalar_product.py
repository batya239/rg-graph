#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import graph_state
import graphine
from sector import Sector
from rggraphenv import abstract_graph_calculator, symbolic_functions


def find_topology_result_converter(shrunk, graph):
    return shrunk, graph


class ScalarProductRuleKey(object):
    """
    used only as a key for hashtable based collections
    """
    def __init__(self, left_momentum, right_momentum):
        self._sp = frozenset((left_momentum, right_momentum))

    def __hash__(self):
        return hash(self._sp)

    def is_external_p_2(self):
        return self._sp == frozenset([0])

    def __eq__(self, other):
        if isinstance(other, ScalarProductRuleKey):
            # noinspection PyProtectedMember
            return self._sp == other._sp
        raise AssertionError()

    def __str__(self):
        return "SPKEY(%s)" % self._sp

    __repr__ = __str__


class ScalarProduct(object):
    def __init__(self, propagator1, propagator2, power=1, sign=1):
        self._propagator1 = propagator1
        self._propagator2 = propagator2
        self._power = power
        self._sign = sign

    def apply(self, sectors_linear_combinations, rules):
        factor = symbolic_functions.CLN_ZERO
        for i in enumerate(self._propagator1):
            for j in enumerate(self._propagator2):
                if i[1] != 0 and j[1] != 0:
                    c = symbolic_functions.cln(i[1] * j[1])
                    key = ScalarProductRuleKey(i[0], j[0])
                    if key.is_external_p_2():
                        factor += c
                    else:
                        factor += rules[key] * c
        result = sectors_linear_combinations
        for i in xrange(self._power):
            result *= factor
        result = result.force_filter_zeros()
        return result if self._sign == 1 else (- result)

    def __str__(self):
        return "SPK(p1=%s, p2=%s, power=%s, sign=%s)" % (self._propagator1, self._propagator2, self._power, self._sign)

    __repr__ = __str__