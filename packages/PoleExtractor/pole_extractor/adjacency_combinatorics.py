__author__ = 'gleb'

import copy

import nickel
import graph_state
import graphine
from graphine import filters
from phi4.graphs import conserv


def unique(seq):
    seen = set()
    return [x for x in seq if str(x) not in seen and not seen.add(str(x))]


def unite(seq):
    """
    turns sequence of sequences in sequence of elements of sequences, e.g.
    [[1, 2, 3], [4, 5], [6,]] -> [1, 2, 3, 4, 5, 6]
    """
    s = copy.deepcopy(seq)
    result = []
    while s:
        result.extend(s.pop(0))
    return result


class UVRelevanceCondition(object):
    def __init__(self, PHI_EXPONENT):
        if PHI_EXPONENT == 4:
            self.relevantGraphsLegsCard = {2, 4}
        elif PHI_EXPONENT == 3:
            self.relevantGraphsLegsCard = {2, 3}
        else:
            self.relevantGraphsLegsCard = set()

    # noinspection PyUnusedLocal
    def isRelevant(self, edgesList, superGraph, superGraphEdges):
        subgraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
        return len(subgraph.edges(subgraph.externalVertex)) in self.relevantGraphsLegsCard


def graph_info(diag):
    """
    FOR UNCOLOURED GRAPHS ONLY. YET.
    """
    result = dict()
    ext = -1

    if isinstance(diag, list):
        c = nickel.Canonicalize(diag)
    elif isinstance(diag, str):
        c = nickel.Canonicalize(nickel.Nickel(string=diag).edges)

    nick = nickel.Nickel(nickel=c.nickel)

    result['external vertex'] = ext
    result['adjacency list'] = copy.deepcopy(nick.edges)
    result['nickel label'] = copy.deepcopy(nick.string)

    result['edges'] = len(result['adjacency list'])
    result['tails'] = len(filter(lambda x: ext in x, result['adjacency list']))

    result['vertices'] = len(set(unite(result['adjacency list']))) - int(result['tails'] > 0)
    result['loops'] = result['edges'] - result['tails'] - result['vertices'] + 1

    vacuum_loop = dict((edge_number, edge) for edge_number, edge in
                       enumerate(result['adjacency list']) if ext not in edge)
    result['conservation laws'] = sorted([sorted(list(law)) for law in list(conserv.Conservations(vacuum_loop))])

    return result


def shrink_relevant_subgraphs(label, PHI_EXPONENT):
    """
    NDiag must be Nickel-permutated
    :param NDiag:
    """

    def internalEdges(graph):
        res = list()
        for edge in graph.allEdges():
            if graph.externalVertex not in edge.nodes:
                res.append(edge)
        return res

    def intersect(graph1, graph2):
        g1 = graphine.Representator.asGraph(internalEdges(graph1), g.externalVertex)
        g2 = graphine.Representator.asGraph(internalEdges(graph2), g.externalVertex)
        v1 = set(g1.vertexes())
        v2 = set(g2.vertexes())
        if 0 == len(v1.intersection(v2)):
            return False
        else:
            return True

    def intersect_w_list(graph, graphlist):
        for g in graphlist:
            if intersect(graph, g):
                return True
        return False

    uv = UVRelevanceCondition(PHI_EXPONENT)

    subgraphUVFilters = (filters.oneIrreducible
                         + filters.noTadpoles
                         + filters.vertexIrreducible
                         + filters.isRelevant(uv))

    g = graphine.Graph(graph_state.GraphState.fromStr(label))
    subgraphsUV = [subg for subg in g.xRelevantSubGraphs(subgraphUVFilters, graphine.Representator.asGraph)]

    subgraph_groupings = []
    current_grouping = map(lambda x: [x[0], [x[1], ]], enumerate(subgraphsUV))
    next_grouping = []
    while True:
        for group in current_grouping:
            for i, subgraph in enumerate(subgraphsUV):
                if i > group[0] and not intersect_w_list(subgraph, group[1]):
                    next_grouping.append(copy.deepcopy([i, group[1] + [subgraph]]))
        subgraph_groupings += copy.deepcopy(current_grouping)
        if len(next_grouping) == 0:
            break
        else:
            del current_grouping[:]
            current_grouping = copy.deepcopy(next_grouping)
            del next_grouping[:]
    shrinking_lists = map(lambda x: x[1], subgraph_groupings)

    result = []
    for grouping in shrinking_lists:
        result.append([grouping, g.batchShrinkToPoint(map(lambda x: internalEdges(x), grouping))])

    return result


