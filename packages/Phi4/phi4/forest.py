#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dimas'


from graphine import filters
import itertools
import r
import graphine
import ir_uv
import graph_state


DEBUG = False


def Delta_IR(co_sub_graph,
             graph,
             k_operation,
             uv_sub_graph_filter,
             description="", use_graph_calculator=True):
    """
    stupid algorithm
    """
    delta_ir = 0
    for forest in _generate_forests(co_sub_graph, graph):
        if DEBUG:
            print "\tFOREST gamma =", co_sub_graph.getPresentableStr(), \
                ", graph =",  graph.getPresentableStr(), \
                ", forest =", map(lambda f: f.getPresentableStr(), forest)
        delta_ir += _calculate_delta_ir(forest, co_sub_graph, graph,
                                        k_operation, uv_sub_graph_filter,
                                        description=description,
                                        use_graph_calculator=use_graph_calculator)
    return delta_ir


def _generate_forests(co_sub_graph, graph):
    forests = list()
    forests.append([])
    forest_generators = [x for x in _x_generate_forests(graph, co_sub_graph)]
    for i in xrange(1, len(forest_generators) + 1):
        for comb in itertools.combinations(forest_generators, i):
            forest = _try_create_forest(comb)
            if forest is not None:
                forests.append(forest)
    return forests


def _calculate_delta_ir(forest, co_sub_graph, graph, k_operation, uv_sub_graph_filter, description="", use_graph_calculator=True):
    forest_extension = [co_sub_graph] + forest
    sign = -1 if len(forest_extension) % 2 == 0 else 1
    f = forest_extension.pop()
    delta_ir = sign * r.KRStar(_remove_tails(graph.shrinkToPoint(f.allEdges())), k_operation, uv_sub_graph_filter,
                               description=description,
                               use_graph_calculator=use_graph_calculator)
    if len(forest_extension):
        prev_f = f
        while len(forest_extension):
            curr_f = forest_extension.pop()
            delta_ir *= (-1) * r.KRStar(_remove_tails(prev_f.shrinkToPoint(curr_f.allEdges())),
                                 k_operation, uv_sub_graph_filter,
                                 description=description,
                                 use_graph_calculator=use_graph_calculator)
            prev_f = curr_f
    return delta_ir


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


def _x_generate_forests(graph, co_sub_graph):

    @filters.graphFilter
    def superGraphFilter(edges_list, _super_graph, _super_graph_edges):
        maybe_spinney_generator = graphine.Graph(edges_list, renumbering=False)
        return maybe_spinney_generator.contains(co_sub_graph) \
               and len(co_sub_graph.allEdges()) != len(maybe_spinney_generator.allEdges()) \
               and len(co_sub_graph.allEdges()) + 1 != len(maybe_spinney_generator.allEdges()) \
               and len(maybe_spinney_generator.allEdges()) + 1 != len(_super_graph_edges)
    return graph.xRelevantSubGraphs(filters.oneIrreducible +
                                    filters.isRelevant(ir_uv.UV_RELEVANCE_CONDITION_4_DIM) +
                                    superGraphFilter,
                                    cutEdgesToExternal=False,
                                    resultRepresentator=graphine.Representator.asGraph)


def _remove_tails(graph):
    with_deleted = graph.deleteEdges(graph.externalEdges())
    to_add = []
    for v in with_deleted.vertices():
        edges_len = len(with_deleted.edges(v))
        if edges_len != 4:
            to_add += map(lambda i: graph_state.Edge((v, -1), colors=(0, 0)), xrange(4 - edges_len))
    return with_deleted.addEdges(to_add)

