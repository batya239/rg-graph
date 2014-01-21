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

    def __init__(self, diagram, k=False, derivative=False):
        assert(isinstance(diagram, graphine.Graph))
        self._diagram = diagram
        self._k = k
        self._derivative = derivative

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

    @staticmethod
    def fromString(s):
        k_operation = False
        d = False
        if s[0] == '(' and s[-1] == ')':
            s = s[1:-1]
            k_operation = True
        if s[0:len(RPrimeTermFactor.DerivativePrefix)] == RPrimeTermFactor.DerivativePrefix:
            s = s[len(RPrimeTermFactor.DerivativePrefix):]
            d = True
        g = graphine.Graph.fromStr(s)
        return RPrimeTermFactor(g, k_operation, d)


def shrinking_groups(graph, PHI_EXPONENT):
    def intersect(graph1, graph2):
        return bool(graph1.vertices().difference({graph1.externalVertex, }).
                    intersection(graph2.vertices().difference({graph2.externalVertex, })))

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


def generate_counterterms(graph, exclusion_groups, PHI_EXPONENT, momentum_derivative=False):
    """
    """
    def add_adjoining_edge(sg, g):
        border_vertices = filter(lambda x: not x == sg.externalVertex,
                                 sum([list(e.nodes) for e in sg.externalEdges()], []))
        border_edges = filter(lambda x: x not in sg.allEdges(),
                              sum([g.edges(v) for v in border_vertices], []))
        return graphine.Graph(sg.allEdges() + [border_edges[0]], renumbering=False)

    def exclude_sg(term, sg):
        if 2 == sg.externalEdgesCount():
            sg2 = add_adjoining_edge(sg, term[1][-1])
            return [(term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True), term[1][-1].shrinkToPoint(sg.internalEdges())]),
                    (-term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True, derivative=True), term[1][-1].shrinkToPoint(sg.internalEdges())]),
                    (term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True, derivative=True), term[1][-1].shrinkToPoint(sg2.internalEdges())])]
        else:
            return [(term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True), term[1][-1].shrinkToPoint(sg.internalEdges())]), ]

    def update_tails(graph, valency):
        vs = graph.vertices() - {graph.externalVertex}
        edges = []
        for v in vs:
            if len(graph.edges(v)) < valency:
                edges += [graph_state.Edge((v, graph.externalVertex))] * (valency - len(graph.edges(v)))
        return graphine.Graph(graph.allEdges() + edges)

    result = []
    for group in exclusion_groups:
        counterterms = [(1, [graph, ]), ]
        for subgraph in group:
            counterterms = sum(map(lambda x: exclude_sg(x, subgraph), counterterms), [])
        for ctm in counterterms:
            ctm[1][-1] = update_tails(ctm[1][-1], PHI_EXPONENT)
            result.append((ctm[0], ctm[1][:-1] + [RPrimeTermFactor(ctm[1][-1])]))
            if 2 == ctm[1][-1].externalEdgesCount():
                result.append((ctm[0], ctm[1][:-1] + [RPrimeTermFactor(ctm[1][-1], derivative=True), 'p^2']))

    if not momentum_derivative:
        return filter(lambda x: 'p^2' not in x[1], result)
    else:
        return filter(lambda y: y is not None, map(lambda x: (x[0], x[1][:-1]) if 'p^2' in x[1] else None, result))


def gen_cts(graph, exclusion_groups, PHI_EXPONENT, momentum_derivative=False):
    """
    """
    def add_adjoining_edge(sg, g):
        border_vertices = filter(lambda x: not x == sg.externalVertex,
                                 sum([list(e.nodes) for e in sg.externalEdges()], []))
        border_edges = filter(lambda x: x not in sg.allEdges(),
                              sum([g.edges(v) for v in border_vertices], []))
        return graphine.Graph(sg.allEdges() + [border_edges[0]], renumbering=False)

    def exclude_sg(term, sg):
        if 2 == sg.externalEdgesCount():
            sg2 = add_adjoining_edge(sg, term[1][-1])
            return [(term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True), term[1][-1].shrinkToPoint(sg.internalEdges())]),
                    (-term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True, derivative=True), term[1][-1].shrinkToPoint(sg.internalEdges())]),
                    (term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True, derivative=True), term[1][-1].shrinkToPoint(sg2.internalEdges())])]
        else:
            return [(term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True), term[1][-1].shrinkToPoint(sg.internalEdges())]), ]

    def update_tails(graph, valency):
        vs = graph.vertices() - {graph.externalVertex}
        edges = []
        for v in vs:
            if len(graph.edges(v)) < valency:
                edges += [graph_state.Edge((v, graph.externalVertex))] * (valency - len(graph.edges(v)))
        return graphine.Graph(graph.allEdges() + edges)

    result = []
    for group in exclusion_groups:
        counterterms = [(1, [graph, ]), ]
        for subgraph in group:
            counterterms = sum(map(lambda x: exclude_sg(x, subgraph), counterterms), [])
            for ctm in counterterms:
                if not momentum_derivative:
                    ctm[1][-1] = update_tails(ctm[1][-1], PHI_EXPONENT)
                result.append((ctm[0], ctm[1][:-1] + [RPrimeTermFactor(ctm[1][-1], derivative=momentum_derivative)]))
    return result