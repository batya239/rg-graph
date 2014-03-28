#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dimas'


from graphine import filters
from rggraphenv import symbolic_functions
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
    stupid algorithm
    """
    delta_ir = symbolic_functions.CLN_ZERO
    if DEBUG:
        debug_line = "D_IR(%s)=" % shrunk.getPresentableStr()
    for forest in _generate_forests(co_sub_graph, graph, r_operator):
        add, d_add = _calculate_delta_ir(forest, co_sub_graph, graph, r_operator)
        delta_ir += add
        if DEBUG:
            debug_line += "+" + d_add
    if DEBUG:
        print debug_line
        print "D_IR(%s)=%s" % (shrunk, delta_ir)
    return delta_ir


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
    sign = symbolic_functions.CLN_MINUS_ONE if len(forest_extension) % 2 == 0 else symbolic_functions.CLN_ONE
    f = forest_extension.pop()

    # delta_ir = sign * r_operator.kr_star(_remove_tails(graph.shrinkToPoint(f.allEdges())))
    delta_ir = sign * symbolic_functions.series(r_operator.kr_star(_remove_tails(graph.shrinkToPoint(f.allEdges()))), symbolic_functions.e, symbolic_functions.CLN_ZERO, 0, True)
    if DEBUG:
        debug_line = "(%s)*kr_star(%s)" % (sign, _remove_tails(graph.shrinkToPoint(f.allEdges())).getPresentableStr())
    else:
        debug_line = None
    if len(forest_extension):
        prev_f = f
        while len(forest_extension):
            curr_f = forest_extension.pop()
            delta_ir *= symbolic_functions.CLN_MINUS_ONE * symbolic_functions.series(r_operator.kr_star(_remove_tails(prev_f.shrinkToPoint(curr_f.allEdges()))), symbolic_functions.e, symbolic_functions.CLN_ZERO, 0, True)
            # delta_ir *= symbolic_functions.CLN_MINUS_ONE * r_operator.kr_star(_remove_tails(prev_f.shrinkToPoint(curr_f.allEdges())))
            if DEBUG:
                debug_line += "*(-kr_star(%s))" % _remove_tails(prev_f.shrinkToPoint(curr_f.allEdges())).getPresentableStr()
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
    @filters.graphFilter
    def superGraphFilter(edges_list, _super_graph, _super_graph_edges):
        maybe_spinney_generator = graphine.Graph(edges_list, renumbering=False)
        return maybe_spinney_generator.contains(co_sub_graph) \
               and len(co_sub_graph.allEdges()) != len(maybe_spinney_generator.allEdges()) \
               and len(co_sub_graph.allEdges()) + 1 != len(maybe_spinney_generator.allEdges()) \
               and len(maybe_spinney_generator.allEdges()) + 1 != len(_super_graph_edges)
    return graph.xRelevantSubGraphs(filters.oneIrreducible +
                                    r_operator.uv_filter +
                                    superGraphFilter,
                                    cutEdgesToExternal=False,
                                    resultRepresentator=graphine.Representator.asGraph)


def _remove_tails(graph):
    with_deleted = graph.deleteEdges(graph.externalEdges())
    graph_str = str(graph)
    arrows_aware = ":" in graph_str and len(graph_str.split(":")[2]) != 0
    arrow = graph_state.Arrow(graph_state.Arrow.NULL) if arrows_aware else None
    to_add = []
    for v in with_deleted.vertices():
        edges_len = len(with_deleted.edges(v))
        if edges_len != 4:
            to_add += map(lambda i: graph_util.new_edge((v, graph.external_vertex), weight=const.ZERO_WEIGHT, arrow=arrow), xrange(4 - edges_len))
    return with_deleted.addEdges(to_add)