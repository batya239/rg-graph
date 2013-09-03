#!/usr/bin/python
# -*- coding: utf8
import copy
import itertools
import os
import shutil
import subprocess
import rggraphutil

__author__ = 'mkompan'

import sys
import graphine
import graph_state
import re
# noinspection PyUnresolvedReferences
import sympy


_MINCER_DEFAULT_TMP_DIR = "/tmp/__mincer1111_O_D_bl_N__"
_MINCER_DIR = _MINCER_DEFAULT_TMP_DIR
_MINCER2_H = "mincer2.h"
_FORM_VERSION = "tform"

_RESULT_REGEXP = re.compile("F\s=(.*);")


def initMincer(mincerDir=_MINCER_DEFAULT_TMP_DIR, useMultiThreading=True):
    _FORM_VERSION = "tform" if useMultiThreading else "form"
    exception = None
    for i in xrange(2):
        try:
            _MINCER_DIR = mincerDir
            os.makedirs(_MINCER_DIR)
            shutil.copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib", _MINCER2_H),
                            os.path.join(_MINCER_DIR, _MINCER2_H))
            return
        except OSError as e:
            disposeMincer()
            exception = e
    raise exception

def disposeMincer():
    shutil.rmtree(_MINCER_DIR)


# noinspection PyUnboundLocalVariable
def isApplicable(graph):
    if graph.getLoopsCount() > 3:
        return False
    edges = graph.allEdges()
    if not len(edges):
        return False
    for e in edges:
        c = e.colors
        if c is None or len(c) != 2:
            return False
        if c[1] != 0 or c[0] != int(c[0]):
            return False
    return True


def calculateGraph(graph):
    t = writeFormFile(graph, _MINCER_DIR)
    if t is None:
        return None
    fileName = t[2]

    #stdout = subprocess.check_output("cd " + _MINCER_DIR + ";" + "form " + fileName, shell=True).replace("\n", '')
    proc = subprocess.Popen("cd " + _MINCER_DIR + ";" + _FORM_VERSION + " " + fileName, shell=True,
                            stdout=subprocess.PIPE)
    proc.wait()
    stdout = proc.stdout.read().replace("\n", "")

    rawResult = _RESULT_REGEXP.findall(stdout)[0]
    rawResult = rawResult.replace("Q.Q", "1").replace("^", "**").replace("ep", "_e")
    rawResult = _replaceZetas(rawResult)
    rawResult = rggraphutil.symbolic_functions._safeIntegerNumerators(rawResult)
    if rawResult.strip() == '0':
        return None
        # noinspection PyUnusedLocal
    _e = rggraphutil.symbolic_functions._getE()
    # noinspection PyUnusedLocal
    _p = rggraphutil.symbolic_functions._getP()
    res = eval(rawResult)
    return res, _calculatePFactor(graph)


def _replaceZetas(rawResult):
    return re.sub('z(\d+)', 'sympy.zeta(\\1)', rawResult)


def _calculatePFactor(graph):
    factor0 = 0
    for e in graph.internalEdges():
        factor0 += e.colors[0]
    return factor0 - graph.getLoopsCount(), - graph.getLoopsCount()

# no signs for momenta at this moment
topologies = {
    'e12-23-3-e-': ('t1', ['Q', 'p1', 'p4', 'p5', 'p2', 'p3', 'Q']),
    'e12-e3-33--': ('t2', ['Q', 'p1', 'p2', 'Q', 'p1', 'p3', 'p4']),
    'e11-22-e-': ('t3', ['Q', 'p1', 'p2', 'p3', 'p4', 'Q']),
    'e12-e3-45-45-5--': ('o4', ['Q', 'p6', 'p7', 'Q', 'p6', 'p1', 'p4', 'p2', 'p3', 'p5']),
    'e12-23-4-45-5-e-': ('la', ['Q', 'p1', 'p6', 'p7', 'p2', 'p5', 'p8', 'p3', 'p4', 'Q']),
    'e12-34-35-4-5-e-': ('be', ['Q', 'p1', 'p5', 'p6', 'p2', 'p8', 'p4', 'p7', 'p3', 'Q']),
    'e12-34-34-e4--': ('bu', ['Q', 'p6', 'p7', 'p1', 'p4', 'p3', 'p5', 'Q', 'p2']),
    'e12-23-34-4-e-': ('fa', ['Q', 'p1', 'p5', 'p6', 'p2', 'p7', 'p4', 'p3', 'Q']),
    'e12-34-34-5-5-e-': ('no', ['Q', 'p1', 'p6', 'p2', 'p7', 'p8', 'p5', 'p3', 'p4', 'Q']),
}

graphs = dict((k, v) for (k, v) in
              map(lambda gs: (gs, graphine.Graph(graph_state.GraphState.fromStr("%s::" % gs))), topologies.keys()))


def _setMomenta(graphName, momentaList):
    graph = graphine.Graph(graph_state.GraphState.fromStr("%s::" % graphName))
    edgesList = list()
    for edge in graph.allEdges(withIndex=True):
        edge_ = copy.copy(edge.underlying)
        idx = edge.index
        edge_.colors = graph_state.Rainbow((momentaList[idx],))
        edgesList.append(edge_)
    return graphine.Graph(graph_state.GraphState(edgesList))


def _findTopology(targetGraph, topologies):
    targetGraphName = targetGraph.getPresentableStr()
    for topology in topologies:
        #print "topology : ", topologies[topology][0]

        modelGraph = _setMomenta(topology, topologies[topology][1])

        internalEdges = modelGraph.internalEdges()

        #graph_ = graphine.Graph(graph_state.GraphState.fromStr("%s::" % graphName))
        n = len(internalEdges) - len(targetGraph.internalEdges())
        if n < 0:
            continue
        elif n == 0:
            if topology == targetGraphName:
                return topologies[topology][0], modelGraph

        for lines in itertools.combinations(internalEdges, n):
            shrunk = modelGraph.batchShrinkToPoint([[x] for x in lines])
            gsString = shrunk.getPresentableStr()
            if targetGraphName == gsString:
                return topologies[topology][0], shrunk
    return None


formTemplate = """
#-
#include mincer2.h
.global
Local F = 1{denom};
Multiply ep^3;
#call integral({topology})
Print +f;
.end
"""


def generateFormFile(topologyType, graphWithMomenta, graphWithWeights):
    denom = ""
    graphWithMomentaAndWeights = graphine.util.merge(graphWithMomenta, graphWithWeights)
    for line in graphWithMomentaAndWeights.internalEdges():
        denom += ''.join(["/%s.%s" % (line.colors[0], line.colors[0])] * line.colors[1])
    return formTemplate.format(denom=denom, topology=topologyType)


def writeFormFile(graph, directory="form_files"):
    ans = _findTopology(graph, topologies)
    if ans is not None:
        topologyType, graphWithMomenta = ans
        fileName = '%s.frm' % graph.getPresentableStr()
        f = open(os.path.join(directory, fileName), 'w+')
        f.write(generateFormFile(topologyType, graphWithMomenta, graph))
        f.close()
        return topologyType, graphWithMomenta, fileName
    else:
        return None


def canCalculateGraphWithMincer(graph):
    for e in graph.allEdges(withIndex=False):
        colors = e.colors
        if colors is not None and colors[0] != 0:
            return False
    return True


def main():
    g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr(sys.argv[1])))
    initMincer()
    calculateGraph(g)
    disposeMincer()


if __name__ == "__main__":
    main()

