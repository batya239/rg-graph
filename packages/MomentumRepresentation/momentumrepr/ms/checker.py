#!/usr/bin/python
# -*- coding: utf8
import graph_state
import graphine
import result_depot
import t_3_groups
import graph_util_ms
from rggraphutil import zeroDict

__author__ = 'dima'


THREE_TAIL_MAPPINGS = None


def init_3tail_mappings():
    three_tail_graphs = t_3_groups.get_all_flat()
    mappings = dict()
    for g in three_tail_graphs:
        mapped_g = graphine.Graph(map(lambda e: e.copy(fields=graph_state.Fields("00")) if e.is_external() else e, g))
        mappings[mapped_g] = g
    assert len(mappings) == len(three_tail_graphs)
    return mappings


def d_minus_tau(graph):
    new_graphs = list()
    graph_edges = graph.edges()
    for e in graph:
        if e.is_external():
            continue
        new_edges = list(graph_edges)
        new_edges.remove(e)
        next_vertex = graph.create_vertex_index()
        new_edges.append(graph_util_ms.new_edge((e.nodes[0], next_vertex),
                                                external_node=graph.external_vertex,
                                                fields=e.fields))
        new_edges.append(graph_util_ms.new_edge((next_vertex, e.nodes[1]),
                                                external_node=graph.external_vertex,
                                                fields=e.fields))
        new_edges.append(graph_util_ms.new_edge((next_vertex, graph.external_vertex),
                                                external_node=graph.external_vertex,
                                                fields=graph_state.Fields.from_str("00")))
        new_g = graphine.Graph(map(lambda e: e.copy(fields=graph_state.Fields("00")) if e.is_external() else e, graphine.Graph(new_edges)))
        new_graphs.append(new_g)
    return new_graphs


def d_omega(graph):
    minimal_passing = graphine.util.find_shortest_momentum_flow(graph)
    new_graphs = list()
    for e, sign in minimal_passing:
        new_edges = list(graph.edges())
        new_edges.remove(e)
        next_vertex = graph.create_vertex_index()
        new_edges.append(graph_util_ms.new_edge((e.nodes[0], next_vertex),
                                                external_node=graph.external_vertex,
                                                fields=e.fields))
        new_edges.append(graph_util_ms.new_edge((next_vertex, e.nodes[1]),
                                                external_node=graph.external_vertex,
                                                fields=e.fields))
        new_edges.append(graph_util_ms.new_edge((next_vertex, graph.external_vertex),
                                                external_node=graph.external_vertex,
                                                fields=graph_state.Fields.from_str("00")))
        new_g = graphine.Graph(map(lambda e: e.copy(fields=graph_state.Fields("00")) if e.is_external() else e, graphine.Graph(new_edges)))
        new_graphs.append((sign, new_g))
    return new_graphs


def _check(graph, operation, do_minus):
    global THREE_TAIL_MAPPINGS
    if THREE_TAIL_MAPPINGS is None:
        THREE_TAIL_MAPPINGS = init_3tail_mappings()
    new_graphs = operation(graph)
    res = zeroDict()
    for x in new_graphs:
        sign = 1
        if isinstance(x, tuple):
            sign = x[0]
            x = x[1]
        for k, v in result_depot.get(THREE_TAIL_MAPPINGS[x]).iteritems():
            if do_minus:
                res[k] -= v * sign
            else:
                res[k] += v * sign
    res = dict(res)
    print res
    return res


def check_tau(graph):
    return _check(graph, d_minus_tau, True)


def check_omega(graph):
    return _check(graph, d_omega, False)


check_tau(graph_util_ms.from_str("e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|Aa_aA|aA|0a|::::"))
print "{-1: -0.04809210156815194+/-5.168366340676857e-06, -3: -0.02083318472401166+/-2.325152255735347e-07, -2: 0.04765734141404776+/-1.0551860073064364e-06}"
print

check_tau(graph_util_ms.from_str("e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|aA_aA|aA|0a|::::"))
print "{-1: -0.019185500074529002+/-5.000004080941667e-06, -3: -0.02083318472401166+/-2.325152255735347e-07, -2: 0.023684062409589292+/-1.0460696376747057e-06}"
print

check_tau(graph_util_ms.from_str("e12|34|34|5|5|e|:0A_aA_aA|Aa_aA|aA_aA|aA|aA|0a|::::"))
print "{-1: -0.02845268069958072+/-1.3176834706980247e-06, -3: 0.0, -2: 0.023973483359882614+/-1.2934249777719677e-07}"
print

check_tau(graph_util_ms.from_str("e12|34|34|5|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|::::"))
print "{-1: -0.10332296242342215+/-2.2562943104779716e-06, -3: 0.0, -2: 0.07192047523603118+/-1.9506410555044536e-07}"
print

check_tau(graph_util_ms.from_str("e12|34|35|4|5|e|:0A_aA_aA|Aa_aA|aA_aA|aA|aA|0a|::::"))
print "{-1: -0.0009253775000150136+/-2.9124858716956124e-06, -3: -0.010416617257037498+/-1.4498191556115113e-07, -2: 0.0044211461441881+/-5.778290308042985e-07}"
print

check_tau(graph_util_ms.from_str("e12|34|35|4|5|e|:0A_aA_aA|aA_aA|Aa_aA|Aa|aA|0a|::::"))
print "{-1: -0.000925464588825621+/-2.9673666301633114e-06, -3: -0.010416608079724166+/-1.451648968569893e-07, -2: 0.004420688718232264+/-5.935532378968051e-07}"
print

check_tau(graph_util_ms.from_str("e12|34|35|4|5|e|:0A_aA_aA|aA_aA|Aa_aA|aA|aA|0a|::::"))
print "{-1: -0.026851757121820644+/-3.2189462110666926e-06, -3: -0.010416608079724166+/-1.451648968569893e-07, -2: 0.02525435105568976+/-6.022138236149414e-07}"
print

check_tau(graph_util_ms.from_str("e12|34|35|4|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|::::"))
print "{-1: -0.02685190942571081+/-3.196899001914477e-06, -3: -0.0104166025196475+/-1.4512502898149286e-07, -2: 0.025254898899682268+/-5.866273531364767e-07}"
print