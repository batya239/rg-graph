__author__ = 'gleb'

import graphine
from graphine import filters
import copy


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


def shrink_relevant_sgs(label, PHI_EXPONENT):
    """
    """
    def intersect(graph1, graph2):
        """
        Check if graph1 & graph2 have joint vertices.
        """
        v1 = set(graphine.Representator.asGraph(graph1.internalEdges(), g.externalVertex).vertices())
        v2 = set(graphine.Representator.asGraph(graph2.internalEdges(), g.externalVertex).vertices())
        if 0 == len(v1.intersection(v2)):
            return False
        else:
            return True

    def update_groupings(group, subgraphs):
        result = []
        for i, sg in enumerate(subgraphs[group[0]:]):
            if not any(map(lambda x: intersect(x, sg), group[1])):
                result.append((i + group[0], group[1] + tuple([sg])))
        return result

    uv = UVRelevanceCondition(PHI_EXPONENT)
    subgraphUVFilters = (filters.oneIrreducible
                         + filters.noTadpoles
                         + filters.vertexIrreducible
                         + filters.isRelevant(uv))

    g = graphine.Graph.fromStr(label)
    subgraphsUV = [subg for subg in g.xRelevantSubGraphs(subgraphUVFilters, graphine.Representator.asGraph)]

    groupings = [(i, tuple([subgraphsUV[i]])) for i in range(len(subgraphsUV))]
    for group in groupings:
        groupings.extend(update_groupings(group, subgraphsUV))

    result = []
    for group in groupings:
        result.append([group[1], g.batchShrinkToPoint(map(lambda x: x.internalEdges(), group[1]))])

    return result