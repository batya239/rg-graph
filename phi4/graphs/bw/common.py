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


class Tree:
    def __init__(self, id):
        self.idx = id
        self.branches = set()

    def setBranches(self, branches):
        self.branches = map(Tree, branches)

    def hasBranch(self, branch):
        if isinstance(branch, Tree):
            id = branch.idx
        else:
            id = branch
        for tBranch in self.branches:
            if id == tBranch.idx:
                return tBranch
        return None

    def __repr__(self):
        result = str(self.idx)


def xTreeDepthFirst(tree):
    if len(tree.branches) == 0:
        yield tree.idx
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
                if tree.hasBranch(line) and line <> branch.idx:
                    tColors[line].append(2)
                elif line == branch.idx:
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

    originalSectorTree = Tree(0)

    for tSector in sectors_as_string.splitlines():
        sector = eval(tSector)
        currentBranch = originalSectorTree
        for subSector in sector:
            pVar, sVars = subSector
            S = set([pVar] + list(sVars))
            if len(currentBranch.branches) == 0:
                currentBranch.setBranches(S)
                #        print currentBranch.branches, len(currentBranch.branches), S
            branch = currentBranch.hasBranch(pVar)
            if branch <> None:
                currentBranch = branch
            else:
                raise Exception, "pvar = %s, svars = %s, branches = %s , tSector = %s, subSector = %s " % (
                    pVar, sVars, currentBranch.branches, tSector, subSector)

    print 'raw sectors count', len([x for x in xTreeDepthFirst(originalSectorTree)])

    SectorTree = copy.deepcopy(originalSectorTree)
    edges_dict = to_edges_dict(g)
    decompositions = dict([(line, []) for line in edges_dict.keys()])
    removeBranches(SectorTree, decompositions, edges_dict)
    print 'unique sectors count', len([x for x in xTreeDepthFirst(SectorTree)])