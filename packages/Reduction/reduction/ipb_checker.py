#!/usr/bin/python
# -*- coding: utf8


import copy
import scalar_product
import sector
import reductor
import logging
import collections
import two_and_three_loops
import four_loops
import graph_state
import graphine
from rggraphutil import VariableAwareNumber


__author__ = 'dima'


SectorAndScalarProducts = collections.namedtuple("SectorAndScalarProducts", ["sector", "sp"])


class DiffInfo(object):
    def __init__(self, sectors_and_sp, enumerated_graph, diff_index):
        self._sectors_and_sp = sectors_and_sp
        self._enumerated_graph = enumerated_graph
        self._diff_index = diff_index

    @property
    def sectors_and_sp(self):
        return self._sectors_and_sp

    def get_presentation(self):
        return "D(%s)/D(k_%s)" % (self._enumerated_graph, self._diff_index)


class IpbChecker(object):
    LOG = logging.getLogger("IpbChecker")
    LOG.setLevel(logging.DEBUG)
    LOG.addHandler(logging.StreamHandler())

    def __init__(self, graph, reductor):
        assert graph.externalEdgesCount() == 2
        self._graph = graph
        self._reductor = reductor
        self._external_momentum = (1, ) + (0, ) * self._graph.getLoopsCount()
        self._minus_external_momentum = (-1, ) + (0, ) * self._graph.getLoopsCount()

    def do_test(self):
        is_ok = True
        for diff in self.x_generate_ipb():
            value = 0
            do_continue = False
            IpbChecker.LOG.info("start analyze diagram, " + diff.get_presentation())
            for a_sector, sp in diff.sectors_and_sp:
                try:
                    IpbChecker.LOG.info("start analyze part, " + str(a_sector) + ", " + str(sp))
                    value += self._reductor.calculate_sector(a_sector, sp)._final_sector_linear_combinations
                except reductor.RuleNotFoundException:
                    IpbChecker.LOG.info("rule not found for " + diff.get_presentation())
                    do_continue = True
                    break
            if do_continue:
                continue
            if value.is_zero():
                IpbChecker.LOG.info("OK " + diff.get_presentation())
            else:
                IpbChecker.LOG.error("FAIL " + diff.get_presentation())
                is_ok = False
        return is_ok

    def x_generate_ipb(self):
        enumerated_graphs = self._reductor.enumerate_graph(self._graph)
        loops_count = self._graph.getLoopsCount()
        for enumerated_graph in enumerated_graphs:
            for loop_index in xrange(1, loops_count + 1):
                yield self.do_diff(enumerated_graph, self._graph, loop_index)

    def do_diff(self, enumerated_graph, weighted_graph, loop_index):

        diff_sum = list()

        affected = list()
        non_affected = list()
        for e, e2 in zip(enumerated_graph.internalEdges(), weighted_graph.internalEdges()):
            if e.colors[1][loop_index] == 0:
                non_affected.append((e.colors, e2.weight))
            else:
                assert abs(e.colors[1][loop_index]) == 1
                affected.append((e.colors, e2.weight))

        for color, weight in affected:
            affected_copy = copy.copy(affected)
            affected_copy.remove((color, weight))
            affected_copy.append((color, weight + 1))
            raw_sector = [0] * self._reductor._all_propagators_count
            for raw_prop in affected_copy + non_affected:
                raw_sector[raw_prop[0][0]] = raw_prop[1].a
            a_sector = sector.Sector(*raw_sector)
            sp = scalar_product.ScalarProduct(self._external_momentum, color[1], sign=color[1][loop_index])
            diff_sum.append((a_sector, sp))

        return DiffInfo(diff_sum, enumerated_graph, loop_index)


ZERO_WEIGHT = VariableAwareNumber("l", 0, 0)
UNIT_WEIGHT = VariableAwareNumber("l", 1, 0)


def init_weight(graph, zero_weight=ZERO_WEIGHT, unit_weight=UNIT_WEIGHT):
    edges = graph.allEdges()
    inited_edges = list()
    for e in edges:
        if e.weight is None:
            weight = zero_weight if graph.external_vertex in e.nodes else unit_weight
            inited_edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge(e.nodes, graph.external_vertex, weight=weight, marker=e.marker, arrow=e.arrow))
        else:
            inited_edges.append(e)
    return graphine.Graph(inited_edges, external_vertex=graph.external_vertex, renumbering=False)


def main():
    for g in generate_graphs():
        IpbChecker(g, LOOPS_TO_REDUCTOR[g.getLoopsCount()]).do_test()


LOOPS_TO_REDUCTOR = {2: two_and_three_loops.TWO_LOOP_REDUCTOR,
                     3: two_and_three_loops.THREE_LOOP_REDUCTOR,
                     4: four_loops.FOUR_LOOP_REDUCTOR}

GRAPHS_BASE = (
    "e111|e|",
    "ee11|ee|",
    "ee11|22|ee|",
    "ee12|e22|e|",
    "e112|22|e|",
    "ee11|22|33|ee|",
    "ee11|23|e33|e|",
    "ee12|ee3|333||",
    "e123|e23|e3|e|",
    "ee12|e33|e33||",
    "e112|e3|e33|e|",
    "ee12|e23|33|e|",
    "ee12|223|3|ee|",
    "ee11|22|33|44|ee|",
    "ee11|22|34|e44|e|",
    "e112|e2|34|e44|e|",
    "ee11|23|e44|e44||",
    "ee11|23|ee4|444||",
    "ee11|23|e34|44|e|",
    "ee11|23|334|4|ee|",
    "ee12|233|34|4|ee|",
    "ee12|223|4|e44|e|",
    "e123|e24|34|e4|e|",
    "e112|34|e34|e4|e|",
    "e112|e3|e34|44|e|",
    "e112|e3|e44|e44||",
    "ee12|334|334||ee|",
    "ee12|ee3|344|44||",
    "ee12|e23|e4|444||",
    "ee12|e34|e34|44||",
    "ee12|e33|e44|44||",
    "ee12|e33|444|e4||",
    "ee12|233|44|e4|e|",
    "ee12|234|34|e4|e|",
    "ee12|334|344|e|e|",
    "ee12|e33|344|4|e|",
    "ee12|e23|44|e44||",
    "ee12|e34|334|4|e|",
    "ee12|e23|34|44|e|",
    "e112|33|e33||",
    "e112|e3|333||",
    "e123|e23|33||",
    "e112|23|33|e|",
)


def generate_graphs():
    graphs = set()
    for gs_str in GRAPHS_BASE:
        g = init_weight(graphine.Graph.fromStr(gs_str, graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG))
        for _g in graphine.momentum.xArbitrarilyPassMomentum(g):
            graphs.add(init_weight(_g))
    return graphs


if __name__ == "__main__":
    print main()