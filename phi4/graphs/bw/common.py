#!/usr/bin/python
# -*- coding: utf8
import copy
import sys
import phi4.graphs.graph_state as graph_state
from phi4.graphs.graphs import Graph


def to_edges_dict(g):
    res = dict()
    lineIdxShift = min(g._internal_edges_dict().keys()) - 1
    vertexIdxShift = 1
    for lineIdx in g._edges_dict().keys():
        res[lineIdx - lineIdxShift] = map(lambda x: x - vertexIdxShift, g._edges_dict()[lineIdx])
    return res


def countEqualSectors(g, sector_strings):
    sectors = dict()
    edges_dict = to_edges_dict(g)

    for tSector in sector_strings.splitlines():
        sector = eval(tSector)
        #    print sector
        decompositions = dict([(line, []) for line in edges_dict.keys()])
        for subsector in sector:
            pvar, svars = subsector
            #        if  isinstance(svars,int):
            #            svars=(svars,)
            #        print pvar, svars
            for line in edges_dict:
                if line in svars:
                    decompositions[line].append(2)
                elif line == pvar:
                    decompositions[line].append(1)
                else:
                    decompositions[line].append(0)
        ColouredLines = list()
        for line in edges_dict:
            ColouredLines.append(graph_state.Edge(edges_dict[line], colors=graph_state.Rainbow(decompositions[line])))
        gstate = graph_state.GraphState(ColouredLines)
        if sectors.has_key(gstate):
            sectors[gstate].append(tSector)
        else:
            sectors[gstate] = [tSector, ]

    print len(sectors.keys())
    for gstate in sectors:
        if len(sectors[gstate]) > 1:
            print sectors[gstate]
            print


class SDTree:
    def __init__(self, pVar, sVars=list(), parent=None):
        self.pVar = pVar
        self.sVars =  sVars
        self.branches = list()
        self.parent = parent
        self.coefficient = 0

    def addBranch(self, pVar, sVars):
        self.branches.append(SDTree(pVar, sVars, self))

    def hasBranch(self, pVar, sVars=None):
        for b in self.branches:
            if b.pVar == pVar and (b.sVars == sVars or sVars == None):
                return True
        return False

    def getBranch(self, pVar, sVars):
        for b in self.branches:
            if b.pVar == pVar and b.sVars == sVars:
                return b
        return None

    def setCoefficient(self, coefficient):
        self.coefficient = coefficient

    def __repr__(self):
        return repr(self.parent) if self.parent else "" + str(self.idx) + str(self.sVars)


def xTreeDepthFirst(tree):
    if len(tree.branches) == 0:
        yield tree.pVar
    else:
        for branch in tree.branches:
            for x in xTreeDepthFirst(branch):
                yield x


def getGraphState(edges_dict, decompositions):
    ColouredLines = list()
    for line in edges_dict:
        ColouredLines.append(graph_state.Edge(edges_dict[line], colors=graph_state.Rainbow(decompositions[line])))
    return graph_state.GraphState(ColouredLines)


def removeBranches(tree, parentColors, edges_dict):
    if len(tree.branches) == 0:
        return
    else:
        uniqueBranches = dict()
        for branch in tree.branches:
            tColors = copy.deepcopy(parentColors)
            for line in tColors.keys():
                if tree.hasBranch(line) and line <> branch.pVar:
                    tColors[line].append(2)
                elif line == branch.pVar:
                    tColors[line].append(1)
                else:
                    tColors[line].append(0)
            gstate = getGraphState(edges_dict, tColors)
            #            print branch, tColors, parentColors, gstate
            if not uniqueBranches.has_key(gstate):
                uniqueBranches[gstate] = (branch, tColors)
        tree.branches = set()
        for (branch, tColors) in uniqueBranches.values():
            removeBranches(branch, tColors, edges_dict)
            tree.branches.add(branch)
        return


def calculate_symmetries(graph_nomenclature, sectors_as_string):
    print "graph nomenclature", graph_nomenclature
    print "raw sectors"
    print sectors_as_string

    g = Graph(graph_nomenclature)

    originalSectorTree = SDTree(0)
    for tSector in sectors_as_string.splitlines():
        sector = eval(tSector)
        currentBranch = originalSectorTree
        for subSector in sector:
            pVar, sVars = subSector
            if not currentBranch.hasBranch(pVar, sVars):
                currentBranch.addBranch(pVar, sVars)
            currentBranch = currentBranch.getBranch(pVar, sVars)

    print 'raw sectors count', len([x for x in xTreeDepthFirst(originalSectorTree)])

    SectorTree = copy.deepcopy(originalSectorTree)
    edges_dict = to_edges_dict(g)
    decompositions = dict([(line, []) for line in edges_dict.keys()])
    removeBranches(SectorTree, decompositions, edges_dict)
    print 'unique sectors count', len([x for x in xTreeDepthFirst(SectorTree)])