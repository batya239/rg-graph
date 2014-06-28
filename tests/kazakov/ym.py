#!/usr/bin/python
import graph_state
from graph_state_builder import gs_builder
import graphine



@graphine.filters.graph_filter
def nonzero_momenta_counterterm(edgesList, superGraph):
    subgraph = graphine.Graph(edgesList, renumbering=False)
    g = superGraph.batch_shrink_to_point([subgraph])
    external_edges = g.external_edges_count
    zero = False
    for node in g.get_bound_vertices():
        count = 0
        for edge in g.edges(node):
            if edge.is_external():
                count += 1
        if count >= external_edges-1:
            zero = True
            break
    return not zero

@graphine.filters.graph_filter
def uv_condition(edgesList, superGraph):
    g = graphine.Graph(edgesList)
    return uv_index(g) >= 0


def dash_irreducible(graph, edges_with_dash):
    edges = list()
    for edge in graph.edges():
        if edge not in edges_with_dash:
            edges.append(edge)
    return graph_state.operations_lib.is_graph_connected(edges)


def uv_index(graph):
    D = 6
    _uv_index = graph.loops_count * D
    # print _uv_index
    dashes = dict()
    for edge in graph.internal_edges:
        # print edge
        _uv_index -= 2
        if edge.e_num != 0:
            if edge.e_num not in dashes:
                dashes[edge.e_num] = list()
            dashes[edge.e_num].append(edge)

    for dash in dashes:
        dashed_lines = dashes[dash]
        if dash_irreducible(graph, dashed_lines):
            if dash < 10:
                _uv_index += 2
            elif dash < 100:
                _uv_index += 4
            else:
                raise NotImplementedError("more than two dashes %s\n%s" %(dash, graph))
    return _uv_index

#
# def is_graph_connected(edges, additional_vertices=set()):
#     """
#     checks that graph is connected
#
#     see get_connected_components
#     """
#
#     external = set([-1])
#     connected = set(edges[0].nodes) - external
#     added = True
#     todo = edges[1:]
#     while added and len(todo) != 0:
#         added = False
#         todo_ = todo
#         todo = list()
#         for edge in todo_:
#             nodes = set(edge.nodes)
#             if len(nodes & connected) != 0:
#                 connected = (connected | nodes) - external
#                 added = True
#             else:
#                 todo.append(edge)
#     return len(todo) == 0 and len(additional_vertices-connected)==0


#another version
#
# def is_graph_connected(edges, additional_vertices=set()):
#     """
#     checks that graph is connected
#
#     see get_connected_components
#     """
#     external = set([-1])
#     connected = [set(edges[0].nodes) - external]
#     added = True
#     for edge in edges[1:]:
#         nodes = set(edge.nodes)
#         updated_components = list()
#         added = False
#         new_connected = list()
#         for component in connected:
#             if len(nodes & component) != 0:
#                 component = (component | nodes) - external
#                 updated_components.append(component)
#                 added = True
#             else:
#                 new_connected.append(component)
#         connected = new_connected
#         if added:
#             new_component = set()
#             for component in updated_components:
#                 new_component = new_component | component
#             connected.append(new_component)
#         else:
#             new_component =  nodes - external
#             connected.append(new_component)
#     return len(connected) == 1 and len(additional_vertices-connected[0])==0