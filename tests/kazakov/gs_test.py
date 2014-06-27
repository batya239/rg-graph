#!/usr/bin/python
import graph_state
import time
import sys
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



# gs = gs_builder.graph_state_from_str("e12|e3|45|46|7|e7|e7||:0_0_0|0_0|0_0|1_0|0|0_0|0_1||")
# gs = gs_builder.graph_state_from_str("e12|e3|34|5|56|7|e7|e|:0_0_0|0_0|0_0|0|0_0|0|0_0|0|0|")
# gs = gs_builder.graph_state_from_str("e12|e3|34|5|56|7|78|9|e9|e|:0_0_0|0_0|0_0|0|0_0|0|0_0|0|0_0|0|")
# gs = gs_builder.graph_state_from_str("e12|e3|34|5|67|68|9|e9|e9||:0_0_0|0_0|0_0|0|0_0|1_0|0|0_0|0_1||")
# gs = gs_builder.graph_state_from_str("e12|e3|45|46|7|78|79||e9|e|:0_0_0|0_0|0_0|1_0|0|0_0|1_0||0_0|0|")
# gs = gs_builder.graph_state_from_str("e12|e3|45|67|e8|68|9|e9|9||:0_0_0|0_0|0_0|12_0|0_0|0_0|0|0_12|0||")
# gs = gs_builder.graph_state_from_str("e12|e3|45|46|7|e8|79|8|9|e|:0_0_0|0_0|1_0|0_2|2|0_1|0_0|0|0|0|")
# gs = gs_builder.graph_state_from_str("e12|34|56|e7|67|e8|8|9|9|e|:0_0_0|0_1|2_0|0_1|0_0|0_0|2|0|0|0|")
# gs = gs_builder.graph_state_from_str("e12|e34|35|6|67|e67||e|:0_0_0|0_0_0|0_0|0|0_0|0_0_0||0|")
# gs = gs_builder.graph_state_from_str("e12|34|35|67|e6|e7|8|8|e|:0_0_0|0_0|0_0|0_0|0_0|0_0|0|0|0|")

gs = gs_builder.graph_state_from_str(sys.argv[1])
print gs

graph = graphine.Graph(gs)
start = time.time()
print "graph UV index: ", uv_index(graph)
connected = graphine.filters.connected
no_tadpoles = graphine.filters.no_tadpoles
one_irreducible = graphine.filters.one_irreducible
print "subgraphs:"
for subgraph in graph.x_relevant_sub_graphs(one_irreducible + no_tadpoles + uv_condition + nonzero_momenta_counterterm):
    print subgraph

print time.time()-start