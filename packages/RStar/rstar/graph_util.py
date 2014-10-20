#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

from graphine import Graph
from rggraphenv import symbolic_functions
from rggraphutil import VariableAwareNumber
import graph_state
import const
import ir_uv
import common


class Factor(object):
    class Externalizer(graph_state.PropertyExternalizer):
        def serialize(self, obj):
            return symbolic_functions.safe_integer_numerators_strong(self.factor)

        def deserialize(self, string):
            return Factor(symbolic_functions.evaluate(string))

    def __init__(self, factor):
        self._factor = factor

    def __cmp__(self, other):
        return cmp(str(self), str(other))

    @property
    def factor(self):
        return self._factor

    def __mul__(self, other):
        return self._factor * other

    __rmul__ = __mul__

    def __str__(self):
        return str(self.factor)

    __repr__ = __str__


class VariableAwareNumberExternalizer(graph_state.PropertyExternalizer):
    def __init__(self, var_name):
        self._var_name = var_name

    def deserialize(self, string):
        pair = eval(string)
        assert len(pair) == 2
        return VariableAwareNumber(self._var_name, pair[0], pair[1])

    def serialize(self, obj):
        return str((obj.a, obj.b))


WEIGHT_ARROW_MARKER_AND_VERTEX_FACTOR_PROPERTIES_CONFIG = \
    graph_state.PropertiesConfig.create(graph_state.PropertyKey(name="weight",
                                                                is_directed=False,
                                                                externalizer=VariableAwareNumberExternalizer("l")),
                                        graph_state.PropertyKey(name="arrow",
                                                                is_directed=True,
                                                                externalizer=graph_state.property_lib.Arrow.Externalizer()),
                                        graph_state.PropertyKey(name="marker",
                                                                is_directed=True,
                                                                externalizer=graph_state.PropertyExternalizer()),
                                        graph_state.PropertyKey(name="factor",
                                                                is_edge_property=False,
                                                                externalizer=Factor.Externalizer()))

new_edge = WEIGHT_ARROW_MARKER_AND_VERTEX_FACTOR_PROPERTIES_CONFIG.new_edge
new_node = WEIGHT_ARROW_MARKER_AND_VERTEX_FACTOR_PROPERTIES_CONFIG.new_node


def shrink_to_point(graph, sub_graphs):
    to_shrink = list()
    to_replace_by_edge = list()
    p2_counts = 0
    for sg in sub_graphs:
        edge = has_momentum_quadratic_divergence(sg)
        if edge is not None:
            to_replace_by_edge.append((edge, sg))
            graph = graph.change(sg.internal_edges, (edge,), renumbering=False)
            p2_counts += 1
        else:
            edge = has_single_arrow(sg, graph)
            if edge is None:
                to_shrink.append(sg)
            else:
                graph = graph.change(sg.internal_edges, (edge, ), renumbering=True)
    shrunk = graph.batch_shrink_to_point(to_shrink)
    shrunk = try_simplify_edges(shrunk)
    return shrunk, p2_counts


def try_simplify_edges(graph):
    for v in graph.vertices:
        if v != graph.external_vertex:
            v_edges = graph.edges(v)
            if len(v_edges) == 2:
                sum_weight = v_edges[0].weight + v_edges[1].weight
                if sum_weight == 0:
                    return graph.shrink_to_point(v_edges)
    return graph


def has_single_arrow(sub_graph, graph):
    numerated_edge = None
    for e in sub_graph:
        if e.arrow is not None and not e.arrow.is_null():
            if numerated_edge is None:
                numerated_edge = e
            else:
                return None
    if numerated_edge is None:
        return None
    if len(sub_graph.get_bound_vertices()) != 2:
        raise common.CannotBeCalculatedError(graph)
    find_edge_to_replace_numerator(numerated_edge, graph, sub_graph.get_bound_vertices())


def find_edge_to_replace_numerator(numerated_edge, graph, border_vertices):
    momentum_passing = filter(lambda e: not e.is_external() and e.marker is not None and e.marker == const.MARKER_1,
                              graph)
    return resolve_arrows(momentum_passing, numerated_edge, border_vertices)


def has_momentum_quadratic_divergence(sub_graph):
    subgraph_uv_index = ir_uv.uv_index(sub_graph)
    if subgraph_uv_index != 2:
        assert subgraph_uv_index < 2
        return None

    border_vertices = sub_graph.get_bound_vertices()
    # assert len(border_vertices) == 2, sub_graph
    if len(border_vertices) != 2:
        raise common.CannotBeCalculatedError(sub_graph)

    graph_str = str(sub_graph)
    arrows_aware = ":" in graph_str and len(graph_str.split(":")[2]) != 0
    arrow = graph_state.Arrow(graph_state.Arrow.NULL) if arrows_aware else None
    return new_edge(tuple(border_vertices), weight=const.NEGATIVE_WEIGHT_EDGE, arrow=arrow)


def graph_from_str(string,
                   do_init_weight=True,
                   zero_weight=const.ZERO_WEIGHT,
                   unit_weight=const.UNIT_WEIGHT,
                   do_init_arrow=False,
                   arrow_lines=None):
    g = Graph(WEIGHT_ARROW_MARKER_AND_VERTEX_FACTOR_PROPERTIES_CONFIG.graph_state_from_str(string))
    if do_init_weight:
        g = init_weight(g, zero_weight, unit_weight)
    if do_init_arrow:
        g = init_arrow(g, arrow_lines)
    return g


def batch_init_edges_weight(graphs, zero_weight=const.ZERO_WEIGHT, unit_weight=const.UNIT_WEIGHT):
    return map(lambda g: init_weight(g, zero_weight, unit_weight), graphs)


def init_weight(graph, zero_weight=const.ZERO_WEIGHT, unit_weight=const.UNIT_WEIGHT):
    edges = graph.edges()
    inited_edges = list()
    for e in edges:
        if e.weight is None:
            weight = zero_weight if graph.external_vertex in e.nodes else unit_weight
            inited_edges.append(new_edge(e.nodes, graph.external_vertex, weight=weight, marker=e.marker, arrow=e.arrow))
        else:
            inited_edges.append(e)
    return Graph(inited_edges, renumbering=False)


def init_arrow(graph, arrow_lines):
    arrow_lines = list(arrow_lines)
    inited_edges = list()

    for e in graph.edges():
        nodes = e.nodes
        if nodes in arrow_lines:
            arrow_lines.remove(nodes)
            inited_edges.append(new_edge(e.nodes,
                                         external_node=graph.external_vertex,
                                         arrow=graph_state.Arrow(graph_state.Arrow.LEFT_ARROW),
                                         weight=e.weight,
                                         marker=e.marker,
                                         edge_id=e.edge_id))
            continue
        swapped_nodes = e.nodes[1], e.nodes[0]
        if swapped_nodes in arrow_lines:
            arrow_lines.remove(swapped_nodes)
            inited_edges.append(new_edge(swapped_nodes,
                                         external_node=graph.external_vertex,
                                         arrow=graph_state.Arrow(graph_state.Arrow.LEFT_ARROW),
                                         weight=e.weight,
                                         marker=e.marker,
                                         edge_id=e.edge_id))
            continue
        else:
            inited_edges.append(new_edge(e.nodes,
                                         external_node=graph.external_vertex,
                                         arrow=graph_state.Arrow(graph_state.Arrow.NULL),
                                         weight=e.weight,
                                         marker=e.marker,
                                         edge_id=e.edge_id))
    return Graph(inited_edges, renumbering=False)


def resolve_arrows(chain_edges, base_edge, border_vertices):
    assert base_edge.arrow is not None and not base_edge.arrow.is_null()
    assert len(border_vertices) == 2

    if len(chain_edges) == 1:
        return base_edge.copy(weight=const.ZERO_WEIGHT)

    border_vertices = tuple(border_vertices)

    chain_edges = list(chain_edges)
    chain_edges.remove(base_edge)

    for n in base_edge.nodes:
        current_n = n
        visited = set()
        while True:
            visited.add(current_n)
            n_edges = graph_state.operations_lib.edges_for_node(chain_edges, current_n)
            if not len(n_edges):
                break
            assert len(n_edges) in (1, 2)
            if len(n_edges) == 2:
                done = False
                for e in n_edges:
                    if e.nodes[1] == e.nodes[0]:
                        n_edges = [e]
                        done = True
                        break
                assert done
            n_edge = n_edges[0]
            if n_edge.arrow is not None and not n_edge.arrow.is_null():
                arrow = base_edge.arrow if border_vertices[0] in visited else - base_edge.arrow
                fictive_edge = new_edge(border_vertices,
                                        weight=const.ZERO_WEIGHT,

                                        arrow=arrow,
                                        external_node=base_edge.external_node,
                                        marker=const.MARKER_1)
                return fictive_edge
            chain_edges.remove(n_edge)
            current_n = n_edge.co_node(current_n)
    return new_edge(border_vertices,
                    weight=const.ZERO_WEIGHT,
                    arrow=base_edge.arrow,
                    external_node=base_edge.external_node,
                    marker=const.MARKER_1)



