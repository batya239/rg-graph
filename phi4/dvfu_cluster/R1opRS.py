#!/usr/bin/python
# -*- coding: utf8
import itertools
import sympy

__author__ = 'mkompan'
import graphine
from graphine import filters

import graph_state
import sys

from uncertainties import ufloat

DEBUG = False

class RelevanceCondition(object):
    relevantGraphsLegsCard = set([4, ])

    # noinspection PyUnusedLocal
    def isRelevant(self, edgesList, superGraph, superGraphEdges):
        subgraph = graphine.Representator.asGraph(edgesList, superGraph.external_vertex)
        return len(subgraph.edges(subgraph.external_vertex)) in self.relevantGraphsLegsCard


phi4 = RelevanceCondition()

subgraphUVFilters = (filters.oneIrreducible
                     + filters.noTadpoles
                     #                     + filters.vertexIrreducible
                     + filters.isRelevant(phi4))
try:
    fileName = sys.argv[1]
except IndexError:
    print "Usage:\n$ python %s <fileName>\n where <fileName> = source file that contains diags\n \
    in a dict {'diag1':[[res1],[err1]], 'diag2':[[res2],[err2]], ...}"%sys.argv[0]
    exit(0)

results = eval(open(fileName).read())

for i in results:
    results[i][0][0] = -results[i][0][0]


def multiply(ans1, ans2):
    #res1, err1 = ans1
    #res2, err2 = ans2
    r1 = ufloat(ans1[0][0],ans1[1][0])
    r2 = ufloat(ans2[0][0],ans2[1][0])
    r = r1* r2

    #res = res1[0] * res2[0]
    #err = (abs(err1[0] / res1[0]) + abs(err1[0] / res1[0])) * res
    #return (res,), (err,)
    return (r.n,), (r.s,)

try:
    results["ee11-ee-"] = [[1.], [1.0e-15]]
    results["ee11-22-ee-"] = multiply(results["ee11-ee-"], results["ee11-ee-"])
    results["ee11-23-e33-e-"] = multiply(results["ee11-ee-"], results["ee12-e22-e-"])
    results["ee11-22-33-ee-"] = multiply(results["ee11-ee-"], results["ee11-22-ee-"])
    results["ee11-22-33-44-ee-"] = multiply(results["ee11-ee-"], results["ee11-22-33-ee-"])
    results["ee11-23-e44-e44--"] = multiply(results["ee11-ee-"], results["ee12-e33-e33--"])
    results["ee11-22-34-e44-e-"] = multiply(results["ee11-ee-"], results["ee11-23-e33-e-"])
    results["ee11-23-e34-44-e-"] = multiply(results["ee11-ee-"], results["ee12-e23-33-e-"])
    results["ee11-23-ee4-444--"] = multiply(results["ee11-ee-"], results["ee12-ee3-333--"])
    results["e112-e2-34-e44-e-"] = multiply(results["ee12-e22-e-"], results["ee12-e22-e-"])
    results["ee11-23-334-4-ee-"] = multiply(results["ee11-ee-"], results["ee12-223-3-ee-"])
    results["ee11-23-344-45-5-ee-"] = multiply(results["ee11-ee-"], results["ee12-233-34-4-ee-"])
    results["ee11-23-e45-e45-55--"] = multiply(results["ee11-ee-"], results["ee12-e34-e34-44--"])
    results["ee11-22-34-445-5-ee-"] = multiply(results["ee11-ee-"], results["ee11-23-334-4-ee-"])
    results["ee11-23-345-45-e5-e-"] = multiply(results["ee11-ee-"], results["ee12-234-34-e4-e-"])
    results["ee11-22-34-e55-e55--"] = multiply(results["ee11-ee-"], results["ee11-23-e44-e44--"])
    results["ee11-23-445-455-e-e-"] = multiply(results["ee11-ee-"], results["ee12-334-344-e-e-"])
    results["ee11-22-33-45-e55-e-"] = multiply(results["ee11-ee-"], results["ee11-22-34-e44-e-"])
    results["e112-e2-34-e45-55-e-"] = multiply(results["ee12-e22-e-"], results["ee12-e23-33-e-"])
    results["e112-e2-33-45-e55-e-"] = multiply(results["ee12-e22-e-"], results["ee11-23-e33-e-"])
    results["ee11-23-ee4-455-55--"] = multiply(results["ee11-ee-"], results["ee12-ee3-344-44--"])
    results["ee11-23-e44-555-e5--"] = multiply(results["ee11-ee-"], results["ee12-e33-444-e4--"])
    results["ee11-23-445-445--ee-"] = multiply(results["ee11-ee-"], results["ee12-334-334--ee-"])
    results["ee12-223-3-45-e55-e-"] = multiply(results["ee12-e22-e-"], results["ee12-223-3-ee-"])
    results["ee11-23-334-5-e55-e-"] = multiply(results["ee11-ee-"], results["ee12-223-4-e44-e-"])
    results["ee11-22-33-44-55-ee-"] = multiply(results["ee11-ee-"], results["ee11-22-33-44-ee-"])
    results["ee11-23-e34-e5-555--"] = multiply(results["ee11-ee-"], results["ee12-e23-e4-444--"])
    results["ee11-23-e44-e55-55--"] = multiply(results["ee11-ee-"], results["ee12-e33-e44-44--"])
    results["ee11-23-344-55-e5-e-"] = multiply(results["ee11-ee-"], results["ee12-233-44-e4-e-"])
    results["ee12-333-345--e55-e-"] = multiply(results["ee12-e22-e-"], results["ee12-ee3-333--"])
    results["ee11-22-34-ee5-555--"] = multiply(results["ee11-ee-"], results["ee11-23-ee4-444--"])
    results["ee11-22-34-e45-55-e-"] = multiply(results["ee11-ee-"], results["ee11-23-e34-44-e-"])
    results["ee11-23-e44-455-5-e-"] = multiply(results["ee11-ee-"], results["ee12-e33-344-4-e-"])
    results["ee11-23-444-455--ee-"] = multiply(results["ee11-ee-"], results["ee11-23-ee4-444--"])
    results["ee11-23-e45-445-5-e-"] = multiply(results["ee11-ee-"], results["ee12-e34-334-4-e-"])
    results["ee11-23-e34-55-e55--"] = multiply(results["ee11-ee-"], results["ee12-e23-44-e44--"])
    results["e112-e2-34-e55-e55--"] = multiply(results["ee12-e22-e-"], results["ee12-e33-e33--"])
    results["ee11-23-e34-45-55-e-"] = multiply(results["ee11-ee-"], results["ee12-e23-34-44-e-"])
    results["ee11-23-334-4-55-ee-"] = multiply(results["ee11-ee-"], results["ee11-23-334-4-ee-"])
except:
    pass

def internalEdges(graph):
    res = list()
    for edge in graph.allEdges():
        if graph.external_vertex not in edge.nodes:
            res.append(edge)
    return res


def checkIntersection(subGraphs):
    """
    subGraphs -- internalEdges of subGraphs
    """
    for subA, subB in itertools.combinations(subGraphs, 2):
        nodesA = set(reduce(lambda x, y: x + y, map(lambda x: list(x.nodes), subA)))
        nodesB = set(reduce(lambda x, y: x + y, map(lambda x: list(x.nodes), subB)))
        if len(set(subA) & set(subB)) != 0 or len(set(nodesA) & set(nodesB)) != 0:
            return False
    return True


def calculateKR1term(subGraphs, shrinkedGraph, results, resultsKR1):
    diag = str(shrinkedGraph)[:-2].replace("|","-")
    if diag not in results:
        raise ValueError("no result for %s " % diag)
    res = ufloat(results[diag][0][0],results[diag][1][0])
    #print "DEBUG: res =", res
    #print results[str(shrinkedGraph)[:-2]]
    for subGraph in subGraphs:
        if str(subGraph) not in resultsKR1:
            resultsKR1[str(subGraph)] = KR1(subGraph, results, resultsKR1)
        res *= - resultsKR1[str(subGraph)]
        if DEBUG: print "calculateKR1term: res, err =",res
    return res.n


def KR1(graph, results, resultsKR1):
    diag = str(graph).replace("|","-")
    if diag in resultsKR1:
        return resultsKR1[diag]

    #res = results[diag[:-2]][0][0]
    res = ufloat(results[diag[:-2]][0][0],results[diag[:-2]][1][0])
    subGraphsUV = [subG for subG in
                   graph.xRelevantSubGraphs(subgraphUVFilters, graphine.Representator.asGraph)]

    subGraphMap = list()
    for subGraph in subGraphsUV:
        intEdges = tuple(internalEdges(subGraph))
        subGraphMap.append((subGraph, intEdges))
    #        subGraphMap[subGraph] = (subGraph, graph.shrinkToPoint(intEdges))
    for i in range(len(subGraphMap)):
        for subGraphs in itertools.combinations(subGraphMap, i + 1):
            if checkIntersection(map(lambda x: x[1], subGraphs)):

                shrinkedGraph = graph.batchShrinkToPoint([x[1] for x in subGraphs])
                subGraphs_ = [x[0] for x in subGraphs]
                term = calculateKR1term(subGraphs_, shrinkedGraph, results, resultsKR1)
                #print graph, subGraphs_, shrinkedGraph, term
                res += term ### WTF?!
    return res


def symmetryCoefficient(graph):
    edges = graph.allEdges()
    unique_edges = dict()
    for idx in edges:
        if idx in unique_edges:
            unique_edges[idx] += 1
        else:
            unique_edges[idx] = 1
    C = sympy.factorial(len(graph.edges(graph.external_vertex))) / len(graph.toGraphState().sortings)

    for idxE in unique_edges:
        C = C / sympy.factorial(unique_edges[idxE])
    return C


maxNLoops = 6

resultsKR1 = dict()
print "{"
for index in results:
    graph = graphine.Graph.fromStr(index.replace("-","|"))
    if graph.getLoopsCount() > maxNLoops:
        continue
    resultsKR1[str(graph)] = KR1(graph, results, resultsKR1)
    res = resultsKR1[str(graph)]
    try:
        err = abs(float(res.s)/float(res.n))
    except ZeroDivisionError:
        err = 0
    print '"%s": \t%s, \t# %s, \t%s \t err_rel: %.3e' % \
        (str(graph), (res.n,res.s), results[str(graph).replace("|","-")[:-2]][0][0], symmetryCoefficient(graph), err)
        #(index, (res.n,res.s), results[str(graph).replace("|","-")[:-2]][0][0], symmetryCoefficient(graph), err)
print "}"
