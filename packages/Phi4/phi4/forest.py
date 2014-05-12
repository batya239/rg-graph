#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dimas'


from graphine import filters
from rggraphenv.symbolic_functions import e, CLN_ONE, CLN_TWO, CLN_MINUS_ONE, CLN_ZERO, series
import itertools
import r
import graphine
import ir_uv
import graph_state
import inject
import const
import graph_util


DEBUG = False


def delta_ir(co_sub_graph, graph, shrunk, r_operator):
    """
    right algorithm
    """
    co_sub_graph, graph = _adjust_for_ir(co_sub_graph, graph)
    delta_ir = CLN_ZERO
    if DEBUG:
        debug_line = "D_IR(%s)=" % shrunk.presentable_str
    for forest in _generate_forests(co_sub_graph, graph, r_operator):
        add, d_add = _calculate_delta_ir(forest, co_sub_graph, graph, r_operator)
        delta_ir += add
        if DEBUG:
            debug_line += "+" + d_add
    if DEBUG:
        print debug_line
        print "D_IR(%s)=%s" % (shrunk, delta_ir)
    return delta_ir


def _adjust_for_ir(co_sub_graph, graph):
    uv_index = ir_uv.uvIndex(co_sub_graph)
    if uv_index == 0:
        return co_sub_graph, graph
    if uv_index == 2:
        border_vertices = co_sub_graph.getBoundVertexes()
        assert len(border_vertices) == 2, ("co_sub_graph: %s\ngraph: %s\nvorder_vertices: %s" % (co_sub_graph, graph, border_vertices))
        for border_vertex in border_vertices:
            edges = graph.edges(border_vertex)
            edges = filter(lambda e: e.is_external() or e not in co_sub_graph.edges(border_vertex), edges)
            only_internal_edges = filter(lambda e: not e.is_external(), edges)
            if len(only_internal_edges) == 1:
                internal_edge = only_internal_edges[0]
                assert len(edges) == 2
                external_edge = filter(lambda e: e != internal_edge, edges)[0]
                new_external_edge = external_edge.copy(node_map={external_edge.internal_node: internal_edge.co_node(external_edge.internal_node)})
                return co_sub_graph.change([external_edge], [internal_edge, new_external_edge], renumbering=False), graph.change([external_edge], [new_external_edge], renumbering=False)
        assert False, ("operation not implemented %s, %s" % (co_sub_graph, graph))
    assert False, ("unsupported uv index" % co_sub_graph)


def _generate_forests(co_sub_graph, graph, r_operator):
    forests = list()
    forests.append([])
    forest_generators = [x for x in _x_generate_forests(graph, co_sub_graph, r_operator)]
    for i in xrange(1, len(forest_generators) + 1):
        for comb in itertools.combinations(forest_generators, i):
            forest = _try_create_forest(comb)
            if forest is not None:
                forests.append(forest)
    return forests


def _calculate_delta_ir(forest,
                        co_sub_graph,
                        graph,
                        r_operator):
    forest_extension = [co_sub_graph] + forest
    sign = CLN_MINUS_ONE if len(forest_extension) % 2 == 0 else CLN_ONE
    f = forest_extension.pop()

    delta_ir = sign * series(r_operator.kr_star(_remove_tails(graph.shrink_to_point(f.edges()))), e, CLN_ZERO, 0, True)
    if DEBUG:
        debug_line = "(%s)*kr_star(%s)" % (sign, _remove_tails(graph.shrink_to_point(f.edges())).presentable_str)
    else:
        debug_line = None
    if len(forest_extension):
        prev_f = f
        while len(forest_extension):
            curr_f = forest_extension.pop()
            delta_ir *= CLN_MINUS_ONE * series(r_operator.kr_star(_remove_tails(prev_f.shrink_to_point(curr_f.edges()))), e, CLN_ZERO, 0, True)
            if DEBUG:
                debug_line += "*(-kr_star(%s))" % _remove_tails(prev_f.shrink_to_point(curr_f.edges())).presentable_str
            prev_f = curr_f
    return delta_ir, debug_line


def _try_create_forest(sub_graphs):
    try:
        return sorted(sub_graphs, _compare)
    except UnComparableException:
        return None


def _compare(sg1, sg2):
    """
    return:
    1  -  sg1 > sg2
    -1 -  sg2 > sg1
    0  -  sg1 >< sg2
    """
    if sg1.contains(sg2) and len(sg1.allEdges()) > len(sg2.allEdges()) + 1:
        return 1
    elif sg2.contains(sg1) and len(sg2.allEdges()) > len(sg1.allEdges()) + 1:
        return -1
    raise UN_COMPARABLE_EXCEPTION


class UnComparableException(BaseException):
    pass


UN_COMPARABLE_EXCEPTION = UnComparableException()


def _x_generate_forests(graph, co_sub_graph, r_operator):

    # noinspection PyUnusedLocal
    @filters.graph_filter
    def superGraphFilter(edges_list, _super_graph):
        maybe_spinney_generator = graphine.Graph(edges_list, renumbering=False)
        return maybe_spinney_generator.contains(co_sub_graph) \
               and len(co_sub_graph.edges()) != len(maybe_spinney_generator.edges()) \
               and len(co_sub_graph.edges()) + 1 != len(maybe_spinney_generator.edges()) \
               and len(maybe_spinney_generator.allEdges()) + 1 != len(_super_graph)

    return graph.x_relevant_sub_graphs(filters.one_irreducible +
                                       r_operator.uv_filter +
                                       superGraphFilter,
                                       cut_edges_to_external=False,
                                       result_representator=graphine.Representator.asGraph)


def _remove_tails(graph):
    with_deleted = graph - graph.external_edges
    graph_str = str(graph)
    arrows_aware = ":" in graph_str and len(graph_str.split(":")[2]) != 0
    arrow = graph_state.Arrow(graph_state.Arrow.NULL) if arrows_aware else None
    to_add = []
    for v in with_deleted.vertices:
        edges_len = len(with_deleted.edges(v))
        if edges_len != 4:
            to_add += map(lambda i: graph_util.new_edge((v, graph.external_vertex), weight=const.ZERO_WEIGHT, arrow=arrow), xrange(4 - edges_len))
    return with_deleted + to_add