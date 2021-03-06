__author__ = 'gleb'

import graphine
from graphine import filters
import graph_state


class RPrimeTermFactor:
    """
    It's a class for storing additional info about diagrams while performing R':
    whether it should be or not derived by p^2,
    whether K must or not be performed over it.
    """
    DerivativePrefix = '{d/dp^2}'

    def __init__(self, diagram, k=False, rprime=True, derivative=False):
        assert (isinstance(diagram, graphine.Graph))
        self._diagram = diagram
        self._k = k
        self._derivative = derivative
        self._rprime = rprime

    def diagram(self):
        return self._diagram

    def __str__(self):
        s = str()
        if self._derivative:
            s += RPrimeTermFactor.DerivativePrefix
        s += str(self._diagram)
        if self._k:
            s = '(' + s + ')'
        return s

    def __repr__(self):
        return str(self)


def shrinking_groups(graph, PHI_EXPONENT):
    def intersect(graph1, graph2):
        return bool(graph1.vertices().difference({graph1.external_vertex, }).
                    intersection(graph2.vertices().difference({graph2.external_vertex, })))

    def update_groupings(group, subgraphs):
        result = []
        for i, sg in enumerate(subgraphs[group[0]:]):
            if not any(map(lambda x: intersect(x, sg), group[1])):
                result.append((i + group[0], group[1] + tuple([sg])))
        return result

    if 3 == PHI_EXPONENT:
        ext_count = (2, 3)
    elif 4 == PHI_EXPONENT:
        ext_count = (2, 4)

    sg_UV_filters = (filters.connected
                     + filters.oneIrreducible
                     + filters.noTadpoles)

    subgraphsUV = filter(lambda x: x.externalEdgesCount() in ext_count,
                         [subg for subg in graph.xRelevantSubGraphs(filters=sg_UV_filters,
                                                                    resultRepresentator=graphine.Representator.asGraph,
                                                                    cutEdgesToExternal=True)])

    groupings = [(i, tuple([subgraphsUV[i]])) for i in range(len(subgraphsUV))]
    for group in groupings:
        groupings.extend(update_groupings(group, subgraphsUV))

    return map(lambda x: x[1], groupings)


def gen_cts(graph, exclusion_groups, PHI_EXPONENT, momentum_derivative=False):
    """
    """
    def shrink_to_nothing(g, sg):
        border_vertices = filter(lambda x: not x == sg.external_vertex,
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

    def exclude_sg(term, sg):
        if 2 == sg.externalEdgesCount():
            return [(term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True), term[1][-1].shrinkToPoint(sg.internalEdges())]),
                    (-term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True, derivative=True),
                    term[1][-1].shrinkToPoint(sg.internalEdges())]),
                    (term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True, derivative=True),
                    shrink_to_nothing(term[1][-1], sg)])]
        else:
            return [(term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True),
                     term[1][-1].shrinkToPoint(sg.internalEdges())]), ]

    def update_tails(graph, valency):
        vs = graph.vertices() - {graph.external_vertex}
        for v in vs:
            while len(graph.edges(v)) < valency:
                graph = graphine.Graph(graph.allEdges() + [graph_state.Edge((v, graph.external_vertex))],
                                       renumbering=False)
        return graph

    result = []
    for group in exclusion_groups:
        counterterms = [((-1) ** len(group), [graph, ]), ]
        for subgraph in group:
            counterterms = sum(map(lambda x: exclude_sg(x, subgraph), counterterms), [])
        for ctm in counterterms:
            if not momentum_derivative:
                ctm[1][-1] = update_tails(ctm[1][-1], PHI_EXPONENT)
            result.append((ctm[0], ctm[1][:-1] + [RPrimeTermFactor(ctm[1][-1], rprime=False,
                                                                   derivative=momentum_derivative)]))
    return result