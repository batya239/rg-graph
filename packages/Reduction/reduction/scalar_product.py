#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import graph_state
import graphine
from sector import Sector


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

    def __eq__(self, other):
        # noinspection PyProtectedMember
        return self._sp == other._sp


class ScalarProduct(object):
    def __init__(self, propagator1, propagator2, power=1, sign=1):
        self._propagator1 = propagator1
        self._propagator2 = propagator2
        self._power = power
        self._sign = sign

    def apply(self, sectors_linear_combinations, rules):
        factor = 0
        for i in enumerate(self._propagator1):
            for j in enumerate(self._propagator2):
                if i[1] != 0 and j[1] != 0:
                    c = i[1] * j[1]
                    key = ScalarProductRuleKey(i[0], j[0])
                    factor += rules[key] * c
        result = sectors_linear_combinations
        for i in xrange(self._power):
            result *= factor
        return result if self._sign == 1 else (- result)

    def _apply_once(self, sector_linear_combinations, apply_rules):
        pass

    def as_key(self):
        return ScalarProductRuleKey(self._propagator1, self._propagator2)