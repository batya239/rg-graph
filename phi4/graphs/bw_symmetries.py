#!/usr/bin/python
# -*- coding: utf8
import copy
import sys
import graph_state
from graphs import Graph

#graph_nomenkl=sys.argv[1]
graph_nomenkl = "e12-23-3-e-"
#sector_strings=open(sys,argv[2]).read()

#indexes = {1:1, 4:2, 5:3, 3:4, 2:5}
indexes = {1:1, 2:2, 3:3, 4:4, 5:5}



sector_strings ="""(5,(1,2,3,4,),), (3,(2,),), (4,(1,),), (3,(1,),)
(5,(1,2,3,4,),), (3,(2,),), (4,(1,),), (1,(3,),), (4,(3,),)
(5,(1,2,3,4,),), (3,(2,),), (4,(1,),), (1,(3,),), (3,(4,),)
(5,(1,2,3,4,),), (3,(2,),), (1,(4,),), (3,(1,),)
(5,(1,2,3,4,),), (3,(2,),), (1,(4,),), (1,(3,),), (4,(3,),)
(5,(1,2,3,4,),), (3,(2,),), (1,(4,),), (1,(3,),), (3,(4,),)
(5,(1,2,3,4,),), (2,(3,),), (4,(1,),), (2,(1,),)
(5,(1,2,3,4,),), (2,(3,),), (4,(1,),), (1,(2,),), (4,(2,),)
(5,(1,2,3,4,),), (2,(3,),), (4,(1,),), (1,(2,),), (2,(4,),)
(5,(1,2,3,4,),), (2,(3,),), (1,(4,),), (2,(1,),)
(5,(1,2,3,4,),), (2,(3,),), (1,(4,),), (1,(2,),), (4,(2,),)
(5,(1,2,3,4,),), (2,(3,),), (1,(4,),), (1,(2,),), (2,(4,),)
(4,(1,2,3,5,),), (2,(1,),), (3,(2,),), (5,(2,),)
(4,(1,2,3,5,),), (2,(1,),), (3,(2,),), (2,(5,),), (5,(3,),)
(4,(1,2,3,5,),), (2,(1,),), (3,(2,),), (2,(5,),), (3,(5,),)
(4,(1,2,3,5,),), (2,(1,),), (2,(3,),), (3,(1,),), (5,(2,),)
(4,(1,2,3,5,),), (2,(1,),), (2,(3,),), (3,(1,),), (2,(5,),), (5,(3,),)
(4,(1,2,3,5,),), (2,(1,),), (2,(3,),), (3,(1,),), (2,(5,),), (3,(5,),)
(4,(1,2,3,5,),), (2,(1,),), (2,(3,),), (1,(3,),), (5,(1,),)
(4,(1,2,3,5,),), (2,(1,),), (2,(3,),), (1,(3,),), (1,(5,),), (5,(2,),)
(4,(1,2,3,5,),), (2,(1,),), (2,(3,),), (1,(3,),), (1,(5,),), (2,(5,),)
(4,(1,2,3,5,),), (1,(2,),), (3,(1,),), (5,(1,),)
(4,(1,2,3,5,),), (1,(2,),), (3,(1,),), (1,(5,),), (5,(2,),)
(4,(1,2,3,5,),), (1,(2,),), (3,(1,),), (1,(5,),), (2,(5,),), (5,(3,),)
(4,(1,2,3,5,),), (1,(2,),), (3,(1,),), (1,(5,),), (2,(5,),), (3,(5,),)
(4,(1,2,3,5,),), (1,(2,),), (1,(3,),), (5,(1,),)
(4,(1,2,3,5,),), (1,(2,),), (1,(3,),), (1,(5,),), (5,(2,),)
(4,(1,2,3,5,),), (1,(2,),), (1,(3,),), (1,(5,),), (2,(5,),)
(3,(1,2,4,5,),), (5,(4,),), (2,(1,),), (5,(2,),), (4,(1,),)
(3,(1,2,4,5,),), (5,(4,),), (2,(1,),), (5,(2,),), (1,(4,),), (4,(2,),)
(3,(1,2,4,5,),), (5,(4,),), (2,(1,),), (5,(2,),), (1,(4,),), (2,(4,),)
(3,(1,2,4,5,),), (5,(4,),), (2,(1,),), (2,(5,),), (4,(1,),), (5,(1,),)
(3,(1,2,4,5,),), (5,(4,),), (2,(1,),), (2,(5,),), (4,(1,),), (1,(5,),)
(3,(1,2,4,5,),), (5,(4,),), (2,(1,),), (2,(5,),), (1,(4,),)
(3,(1,2,4,5,),), (5,(4,),), (1,(2,),), (5,(1,),), (4,(1,),)
(3,(1,2,4,5,),), (5,(4,),), (1,(2,),), (5,(1,),), (1,(4,),)
(3,(1,2,4,5,),), (5,(4,),), (1,(2,),), (1,(5,),), (5,(2,),)
(3,(1,2,4,5,),), (5,(4,),), (1,(2,),), (1,(5,),), (2,(5,),)
(3,(1,2,4,5,),), (4,(5,),), (4,(1,),), (4,(2,),), (5,(2,),)
(3,(1,2,4,5,),), (4,(5,),), (4,(1,),), (4,(2,),), (2,(5,),)
(3,(1,2,4,5,),), (4,(5,),), (4,(1,),), (2,(4,),)
(3,(1,2,4,5,),), (4,(5,),), (1,(4,),), (2,(1,),)
(3,(1,2,4,5,),), (4,(5,),), (1,(4,),), (1,(2,),), (4,(2,),), (5,(2,),)
(3,(1,2,4,5,),), (4,(5,),), (1,(4,),), (1,(2,),), (4,(2,),), (2,(5,),)
(3,(1,2,4,5,),), (4,(5,),), (1,(4,),), (1,(2,),), (2,(4,),)
(2,(1,3,4,5,),), (4,(1,),), (5,(3,),), (5,(4,),)
(2,(1,3,4,5,),), (4,(1,),), (5,(3,),), (4,(5,),), (5,(1,),)
(2,(1,3,4,5,),), (4,(1,),), (5,(3,),), (4,(5,),), (1,(5,),)
(2,(1,3,4,5,),), (4,(1,),), (3,(5,),), (4,(3,),), (3,(1,),)
(2,(1,3,4,5,),), (4,(1,),), (3,(5,),), (4,(3,),), (1,(3,),)
(2,(1,3,4,5,),), (4,(1,),), (3,(5,),), (3,(4,),)
(2,(1,3,4,5,),), (1,(4,),), (5,(3,),), (5,(1,),)
(2,(1,3,4,5,),), (1,(4,),), (5,(3,),), (1,(5,),), (5,(4,),)
(2,(1,3,4,5,),), (1,(4,),), (5,(3,),), (1,(5,),), (4,(5,),)
(2,(1,3,4,5,),), (1,(4,),), (3,(5,),), (3,(1,),)
(2,(1,3,4,5,),), (1,(4,),), (3,(5,),), (1,(3,),), (4,(3,),)
(2,(1,3,4,5,),), (1,(4,),), (3,(5,),), (1,(3,),), (3,(4,),)
(1,(2,3,4,5,),), (5,(4,),), (3,(2,),), (5,(3,),), (4,(3,),)
(1,(2,3,4,5,),), (5,(4,),), (3,(2,),), (5,(3,),), (3,(4,),)
(1,(2,3,4,5,),), (5,(4,),), (3,(2,),), (3,(5,),), (5,(2,),)
(1,(2,3,4,5,),), (5,(4,),), (3,(2,),), (3,(5,),), (2,(5,),)
(1,(2,3,4,5,),), (5,(4,),), (2,(3,),), (5,(2,),), (4,(2,),)
(1,(2,3,4,5,),), (5,(4,),), (2,(3,),), (5,(2,),), (2,(4,),)
(1,(2,3,4,5,),), (5,(4,),), (2,(3,),), (2,(5,),), (5,(3,),)
(1,(2,3,4,5,),), (5,(4,),), (2,(3,),), (2,(5,),), (3,(5,),)
(1,(2,3,4,5,),), (4,(5,),), (4,(3,),), (4,(2,),), (5,(2,),)
(1,(2,3,4,5,),), (4,(5,),), (4,(3,),), (4,(2,),), (2,(5,),)
(1,(2,3,4,5,),), (4,(5,),), (4,(3,),), (2,(4,),)
(1,(2,3,4,5,),), (4,(5,),), (3,(4,),), (3,(2,),), (4,(2,),), (5,(2,),)
(1,(2,3,4,5,),), (4,(5,),), (3,(4,),), (3,(2,),), (4,(2,),), (2,(5,),)
(1,(2,3,4,5,),), (4,(5,),), (3,(4,),), (3,(2,),), (2,(4,),)
(1,(2,3,4,5,),), (4,(5,),), (3,(4,),), (2,(3,),)
"""

values_strings = """0.185933, 8.33992e-06
0.0771765, 6.35586e-06
0.160559, 6.84334e-06
0.169108, 6.90099e-06
0.047507, 5.22048e-06
0.0854345, 7.16423e-06
0.185377, 8.67771e-06
0.0768433, 6.21245e-06
0.16082, 6.69834e-06
0.174461, 7.43351e-06
0.0476794, 5.21288e-06
0.0889825, 7.348e-06
0.0487063, 5.42831e-06
0.0793393, 6.42214e-06
0.0919423, 7.58557e-06
0.0771758, 6.33318e-06
0.0475048, 5.21355e-06
0.0854331, 7.19841e-06
0.0473423, 5.21676e-06
0.0771516, 6.51825e-06
0.0889602, 7.74436e-06
0.0506032, 5.62351e-06
0.086604, 7.34087e-06
0.0812145, 6.93006e-06
0.0771718, 6.45465e-06
0.158463, 6.20843e-06
0.187733, 7.74834e-06
0.174464, 7.03668e-06
0.0794729, 6.31509e-06
0.0482775, 5.19181e-06
0.0768393, 6.03652e-06
0.0768283, 6.33402e-06
0.0482676, 5.23963e-06
0.0794613, 6.59082e-06
0.0464172, 5.07609e-06
0.0922194, 7.76848e-06
0.0922235, 7.83983e-06
0.0464247, 4.98391e-06
0.174173, 7.24222e-06
0.169066, 6.79054e-06
0.0922275, 7.63029e-06
0.0464175, 5.07565e-06
0.0768286, 6.31213e-06
0.0775485, 6.31006e-06
0.0501915, 5.43637e-06
0.174464, 6.98736e-06
0.0889634, 7.67201e-06
0.0476693, 5.12385e-06
0.0854377, 7.20439e-06
0.0475086, 5.16098e-06
0.169104, 6.55256e-06
0.187729, 7.63194e-06
0.158468, 6.19649e-06
0.0768296, 6.31448e-06
0.187416, 7.71152e-06
0.0771754, 6.30206e-06
0.159073, 5.89738e-06
0.0444124, 4.98912e-06
0.0854349, 7.45543e-06
0.0919276, 8.1402e-06
0.0500101, 5.60891e-06
0.044555, 4.97941e-06
0.0952034, 8.42933e-06
0.154014, 7.04483e-06
0.0780296, 6.76617e-06
0.174461, 7.8241e-06
0.187726, 8.73993e-06
0.158466, 6.70091e-06
0.0771757, 6.59133e-06
0.0809068, 6.95289e-06
0.0565039, 6.40139e-06
0.0810448, 6.95963e-06
"""

g = Graph(graph_nomenkl)


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
        self.cnt=1

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
        return str(self.idx)


def xTreeDepthFirst(tree, multiplier=1):
    if len(tree.branches) == 0:
        yield (tree, multiplier*tree.cnt)
    else:
        for branch in tree.branches:
            for x in xTreeDepthFirst(branch, multiplier*tree.cnt):
                yield x


def getGraphState(edges_dict, decompositions):
    ColouredLines = list()
    for line in edges_dict:
        ColouredLines.append(graph_state.Edge(edges_dict[line], colors=graph_state.Rainbow(decompositions[line])))
    gstate = graph_state.GraphState(ColouredLines)
    return gstate


def removeBranches( tree, parentColors, edges_dict, depth=-1):
    if depth == 0:
        return
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
                uniqueBranches[gstate] = [branch, tColors, 1]
            else:
                uniqueBranches[gstate][2]+=1

        tree.branches=set()
        for (branch, tColors, cnt) in uniqueBranches.values():
            removeBranches(branch, tColors, edges_dict, depth - 1)
            branch.cnt=cnt
            tree.branches.add(branch)
        return



originalSectorTree = Tree(0)

iii = 0
for tSector in sector_strings.splitlines():
    sector = eval(tSector)
    values = eval(values_strings.splitlines()[iii])
    iii += 1
    currentBranch = originalSectorTree
    for subsector in sector:
        pvar, svars = subsector
        pvar=indexes[pvar]
        svars=[indexes[x] for x in svars]
        S = set([pvar] + list(svars))
        if len(currentBranch.branches) == 0:
            currentBranch.setBranches(S)
        #        print currentBranch.branches, len(currentBranch.branches), S
        branch = currentBranch.hasBranch(pvar)
        if branch <> None:
            currentBranch = branch
        else:
            raise Exception, "pvar = %s, svars = %s, branches = %s , tSector = %s, subsector = %s " % (
            pvar, svars, currentBranch.branches, tSector, subsector)
    currentBranch.sector=sector
    currentBranch.values=values

print len([x for x in xTreeDepthFirst(originalSectorTree)])

SectorTree = copy.deepcopy(originalSectorTree)
edges_dict = to_edges_dict(g)
decompositions = dict([(line, []) for line in edges_dict.keys()])
removeBranches(SectorTree, decompositions, edges_dict, -1)
print len([x for x in xTreeDepthFirst(SectorTree)])
sum = 0
for (sector, multiplier) in xTreeDepthFirst(originalSectorTree):
    sum += multiplier * sector.values[0]
print sum
sum = 0
for (sector, multiplier) in xTreeDepthFirst(SectorTree):
    sum += multiplier * sector.values[0]
print sum
