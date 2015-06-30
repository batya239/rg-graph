#!/usr/bin/python
# -*- coding: utf8
import graphine
import itertools
from momentumrepr import uv
import collections
import algebra
import integration
import graph_util_ms
import graph_state
import p2_rules
from graph_state import operations_lib
from rggraphutil import zeroDict, emptyListDict

__author__ = 'dima'


no_tadpoles = graphine.filters.no_tadpoles
one_irreducible = graphine.filters.one_irreducible


VertexFactor = collections.namedtuple("VertexFactor", ["c", "param"])
PARAM_PROP = "D"
PARAM_P2 = "P2"
PARAM_T = "T"


def compound_kr1(graphs_with_sym_coefficients):
    result = list()
    for g, sc in graphs_with_sym_coefficients:
        result += kr1(g, sc)

    result_dict = collections.defaultdict(lambda : None)
    for g, c in result:
        result_dict[g] += c
    result = result_dict.items()

    p2_grouping = emptyListDict()
    for x in result:
        p2_count = 0
        for v in x[0].vertices:
            if v.factor == PARAM_P2:
                p2_count += 1
        p2_grouping[p2_count].append(x)

    result = list()
    for k, v in p2_grouping.items():
        if k == 0:
            result += v
        else:
            result += compactify(v, k)

    quadratic_div = None
    for (g, _) in graphs_with_sym_coefficients:
        if quadratic_div is None:
            quadratic_div = g.external_edges_count == 2
        else:
            assert quadratic_div == (g.external_edges_count == 2)

    return result


def compactify(graphs_with_coefficient, p2_count):
    by_basement = emptyListDict()
    for g, c in graphs_with_coefficient:
        by_basement[find_basement(g)].append((g, c))

    class IdWrapper(object):
        def __init__(self, e):
            self.e = e

        def __hash__(self):
            return hash(self.e.edge_id)

        def __eq__(self, other):
            return self.e.edge_id == other.e.edge_id

    def produce_graphs_from_base(base):
        production = zeroDict()
        for comb in itertools.product(base.internal_edges, repeat=p2_count):
            comb = map(lambda e: IdWrapper(e), comb)
            occurrences = zeroDict()
            for e in comb:
                occurrences[e] += 1

            new_edges = list(base.edges())
            coeff = (-1) ** len(comb)
            for e, c in occurrences.iteritems():
                e = e.e
                coeff *= c
                new_edges.remove(e)

                nodes_slice = [e.nodes[0]] + map(lambda i: graph_util_ms.MS_GRAPH_CONFIG.new_node(base.create_vertex_index(), factor=PARAM_P2), xrange(c)) + [e.nodes[1]]
                for i in xrange(c + 1):
                    new_edges.append(graph_util_ms.MS_GRAPH_CONFIG.new_edge((nodes_slice[i], nodes_slice[i + 1]), fields=e.fields))
            production[graphine.Graph(new_edges)] += coeff
        return dict(production)

    result = list()
    for base, graphs in by_basement.iteritems():
        pre_production = collections.defaultdict(lambda: None)
        for g, c in graphs:
            pre_production[g] += c
        pre_production = dict(pre_production)
        production = produce_graphs_from_base(base)
        coef = divide(pre_production, production)
        union_coefficient = coef
        # for g, v in production.iteritems():
        #     union_coefficient += v * coef
        result.append((base, union_coefficient, p2_count))
    return result


def divide(dict1, dict2):
    assert len(dict1) == len(dict2), "graph set isn't complete for compound_kr1()"
    main_div = None
    for k, v1 in dict1.iteritems():
        v2 = dict2[k]
        cur_div = v1 / v2
        if main_div is None:
            main_div = cur_div
        else:
            assert main_div == cur_div, "main = %s, cur = %s, rel = %s" % (main_div, cur_div, (main_div.as_ginac()/cur_div.as_ginac()).simplify_indexed())
    return main_div


def find_basement(graph):
    edges = list(graph.edges())
    for v in graph.vertices:
        if v.factor == PARAM_P2:
            remove_edge(edges, v)
    return graphine.Graph(edges)


def kr1(graph, sym_coefficient=1):
    raw_result = zeroDict()
    uv_subgraphs = [x for x in graph.x_relevant_sub_graphs(one_irreducible + no_tadpoles + uv.uv_condition)]
    for i in xrange(1, len(uv_subgraphs) + 1):
        for comb in itertools.combinations(uv_subgraphs, i):
            if i == 1 or not graphine.util.has_intersecting_by_vertices_graphs(comb):
                shrunk, new_vertices, vertex_mappings = graph.batch_shrink_to_point(comb, with_aux_info=True)
                shrunk = [shrunk]
                for sg in comb:
                    v = find_node(sg, vertex_mappings)
                    shrunk = reduce(lambda l, g_: l + process_vertex(g_, sg, v), shrunk, list())
                shrunk = map(post_process_graph, shrunk)
                for pair in shrunk:
                    raw_result[pair] += (-1) ** len(comb)

    result = [(graph, algebra.Unit * sym_coefficient)]
    for ((g, base_c), count) in raw_result.items():
        result.append((graphine.Graph(g.edges()), base_c * (count * sym_coefficient)))
    return result


def kr1_with_rules(graph, sym_coefficient=1):
    result_dict = collections.defaultdict(lambda : None)

    def remove_external_field(e):
        if not e.is_external():
            return e
        return e.copy(fields=graph_state.Fields("00"))

    for g, c in kr1(graph, sym_coefficient=sym_coefficient):
        contains_p2 = False
        for v in g.vertices:
            if v.factor is not None:
                assert v.factor == PARAM_P2
                contains_p2 = True
                break

        if contains_p2:
            for new_g, new_c in p2_rules.find(g).iteritems():
                result_dict[new_g] += algebra.Number(new_c) * c
        else:
            result_dict[graphine.Graph(map(remove_external_field, g))] += c

    return list(result_dict.iteritems())


def post_process_graph(g):
    c = algebra.Unit
    p2_set = set()
    t_set = set()
    prop_set = set()
    for v in g.vertices:
        factor = v.factor
        if factor is not None:
            c *= factor.c
            if factor.param == PARAM_P2:
                p2_set.add(v)
            elif factor.param == PARAM_T:
                t_set.add(v)
            elif factor.param == PARAM_PROP:
                prop_set.add(v)
            else:
                raise AssertionError()

    new_edges = list()
    for e in g:
        new_e = e
        for n in e.nodes:
            if n in p2_set:
                new_n = n.copy(factor=PARAM_P2)
                new_e = new_e.copy(node_map={n: new_n})
            elif n in t_set:
                new_n = n.copy(factor=None)
                new_e = new_e.copy(node_map={n: new_n})
        new_edges.append(new_e)

    for v in prop_set:
        remove_edge(new_edges, v)

    return graphine.Graph(new_edges), c


def remove_edge(graph_edges, v):
    edges = operations_lib.edges_for_node(graph_edges, v)
    assert len(edges) == 2
    v1 = edges[0].co_node(v)
    new_e = edges[1].copy(node_map={v: v1})
    for e in edges:
        graph_edges.remove(e)
    graph_edges.append(new_e)


def find_node(sg, vertex_mappings):
    for e in sg:
        return vertex_mappings.mapping[e.internal_nodes[0]]
    raise AssertionError()


def process_vertex(shrunk_graph, sg, vertex):
    uv_index = uv.uv_index(sg)
    if uv_index == 0:
        a = algebra.KR1(sg, operation="log")
        g1 = copy_graph_with_node(shrunk_graph, vertex, VertexFactor(a, PARAM_T))
        return [g1]
    else:
        # a*p2+b*iw+c*tau = -b*(p^2-iw+tau33)+(a+b)*p^2+(b+c)*tau
        b = algebra.KR1(sg, operation="iw")
        a = algebra.KR1(sg, operation="p2")
        c = algebra.KR1(sg, operation="tau")

        g1 = copy_graph_with_node(shrunk_graph, vertex, VertexFactor(- b, PARAM_PROP))
        g2 = copy_graph_with_node(shrunk_graph, vertex, VertexFactor(a + b, PARAM_P2))
        g3 = copy_graph_with_node(shrunk_graph, vertex, VertexFactor(b + c, PARAM_T))
        return [g1, g2, g3]


def copy_graph_with_node(graph, node_ixd, factor):
    new_edges = list()
    for e in graph:
        do_continue = False
        for n in e.nodes:
            if n == node_ixd:
                new_n = n.copy(factor=factor)
                new_edges.append(e.copy(node_map={n: new_n}))
                do_continue = True
                break
        if do_continue:
            continue
        new_edges.append(e)
    return graphine.Graph(new_edges, renumbering=False)