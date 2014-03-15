#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dimas'


import itertools
import sector
from rggraphutil import VariableAwareNumber


def calculate_graph_p_factor(graph):
    factor0 = 0
    arrow_factor = 0
    for e in graph.internalEdges():
        arrow_factor += 1 if e.arrow is not None and not e.arrow.is_null() else 0
        factor0 += e.weight.a
    arrow_factor /= 2
    f = VariableAwareNumber("l", factor0 - graph.getLoopsCount() - arrow_factor, - graph.getLoopsCount())
    return f


def find_topology_for_graph(graph, topologies, result_converter):
    target_graph_name = graph.getPresentableStr()
    for topology in topologies:
        internal_edges = topology.internalEdges()
        n = len(internal_edges) - len(graph.internalEdges())
        if n < 0:
            continue
        elif n == 0:
            if topology.getPresentableStr() == target_graph_name:
                return result_converter(topology, graph)
        for lines in itertools.combinations(internal_edges, n):
            shrunk = topology.batchShrinkToPoint([[x] for x in lines])
            gs_as_str = shrunk.getPresentableStr()
            if target_graph_name == gs_as_str:
                return result_converter(shrunk, graph)
    return None


def choose_max(sectors):
    assert len(sectors)
    return sorted(sectors, cmp=_compare)[-1]


def _compare(sector1, sector2):
    """
    Laporta comparator
    """

    n1 = len(filter(lambda i: i != 0, sector1.propagators_weights))
    n2 = len(filter(lambda i: i != 0, sector2.propagators_weights))
    sub = n1 - n2
    if sub != 0:
        return sub
    # md1 = reduce(lambda j, i: j + (i if i > 0 else 0), sector1.propagators_weights)
    # md2 = reduce(lambda j, i: j + (i if i > 0 else 0), sector2.propagators_weights)
    # sub = md1 - md2
    # if sub != 0:
    #     return sub
    max1 = max(sector1.propagators_weights)
    max2 = max(sector2.propagators_weights)
    sub = max1 - max2
    return sub

def _compare_key(sector_key1, sector_key2):
    positive_cnt1 = reduce(lambda a, b: a + int(b == sector.SectorRuleKey.PROPAGATOR_CONDITION_POSITIVE), sector_key1.initial_propagators_condition, 0)
    positive_cnt2 = reduce(lambda a, b: a + int(b == sector.SectorRuleKey.PROPAGATOR_CONDITION_POSITIVE), sector_key2.initial_propagators_condition, 0)