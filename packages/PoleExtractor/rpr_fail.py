__author__ = 'gleb'

import graphine
from graphine import filters
import graph_state


def add_adjoining_edge(sg, g):
    border_vertices = filter(lambda x: not x == sg.externalVertex,
                             sum([list(e.nodes) for e in sg.externalEdges()], []))
    border_edges = filter(lambda x: x not in sg.allEdges() and x in g.internalEdges(),
                          sum([g.edges(v) for v in border_vertices], []))
    return graphine.Graph(sg.allEdges() + [border_edges[0]], renumbering=False)


def shrink_to_nothing(g, sg):
    border_vertices = filter(lambda x: not x == sg.externalVertex,
                             sum([list(e.nodes) for e in sg.externalEdges()], []))
    border_edges = filter(lambda x: x not in sg.allEdges() and x in g.internalEdges(),
                          sum([g.edges(v) for v in border_vertices], []))

    adj_edge = border_edges[0]
    adj_vertex = filter(lambda x: x not in sg.vertices(), adj_edge.nodes)[0]

    sg_adj = graphine.Graph(sg.allEdges() + [adj_edge], renumbering=False)

    g_shrunk = g.shrinkToPoint(sg_adj.internalEdges())
    shrunk_vertex = filter(lambda x: x not in g.vertices(), g_shrunk.vertices())[0]

    es = [graph_state.Edge(nodes=tuple(map(lambda x: adj_vertex if x == shrunk_vertex else x, e.nodes)),
                           fields=e.fields,
                           colors=e.colors,
                           edge_id=e.edge_id) for e in g_shrunk.edges(shrunk_vertex)]

    return g_shrunk.change(edgesToRemove=g_shrunk.edges(shrunk_vertex), edgesToAdd=es, renumbering=False)


g = graphine.Graph.fromStr('e12|23|4|e5|55||')
ext_count = (2, 3)
sg_UV_filters = (filters.connected
                 + filters.oneIrreducible
                 + filters.noTadpoles)

subgraphsUV = filter(lambda x: x.externalEdgesCount() in ext_count,
                     [subg for subg in g.xRelevantSubGraphs(filters=sg_UV_filters,
                                                            resultRepresentator=graphine.Representator.asGraph,
                                                            cutEdgesToExternal=True)])

print shrink_to_nothing(g, subgraphsUV[0]).shrinkToPoint(subgraphsUV[1].internalEdges())
