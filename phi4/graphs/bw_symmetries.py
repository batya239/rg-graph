#!/usr/bin/python
# -*- coding: utf8
import copy
import sys
import re
import os
import graph_state
from graphs import Graph


bw_file = sys.argv[1]
regex = re.match('^(.*)_([ABCX])\.py', bw_file)

if regex:
    graph_nomenkl = os.path.basename(regex.groups()[0])
    strategy = regex.groups()[1]
else:
    print "wrong format: pwd/e12-23-3-e-_A.py"
    sys.exit(1)



exec(open(bw_file).read())
#indexes = {1:1, 4:2, 5:3, 3:4, 2:5}
#indexes = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
indexes = dict(zip(*(range(0,10),range(0,10))))


g = Graph(graph_nomenkl)


def to_edges_dict(g):
    res = dict()
#    lineIdxShift = min(g._internal_edges_dict().keys()) - 1
    lineIdxShift=0
    vertexIdxShift = 1
    for lineIdx in g._edges_dict().keys():
        res[lineIdx - lineIdxShift] = map(lambda x: x - vertexIdxShift, g._edges_dict()[lineIdx])
    return res


class Tree:
    def __init__(self, id):
        self.idx = id
        self.branches = set()
        self.cnt = 1

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


def xTreeDepthFirst(tree, multiplier=1, parents=list()):
    if len(tree.branches) == 0:
        yield (tree, multiplier * tree.cnt, parents)
    else:
        for branch in tree.branches:
            for x in xTreeDepthFirst(branch, multiplier * tree.cnt, parents=parents+[(tree.idx, map(lambda x:x.idx, tree.branches))]):
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
                uniqueBranches[gstate][2] += 1

        tree.branches = set()
        for (branch, tColors, cnt) in uniqueBranches.values():
            removeBranches(branch, tColors, edges_dict, depth - 1)
            branch.cnt = cnt
            tree.branches.add(branch)
        return



originalSectorTree = Tree(0)

iii = 0
for tSector in sector_strings[0].splitlines():
    if len(tSector)==0:
        continue
    sector = eval(tSector)
    values = eval(values_strings[0].splitlines()[iii])
    iii += 1
    currentBranch = originalSectorTree
    for subsector in sector:
        pvar, svars = subsector
        pvar = indexes[pvar]
        svars = [indexes[x] for x in svars]
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
    currentBranch.sector = sector
    currentBranch.values = values

print len([x for x in xTreeDepthFirst(originalSectorTree)])

SectorTree = copy.deepcopy(originalSectorTree)
edges_dict = to_edges_dict(g)
decompositions = dict([(line, []) for line in edges_dict.keys()])
removeBranches(SectorTree, decompositions, edges_dict, -1)
print len([x for x in xTreeDepthFirst(SectorTree)])
sum = 0
for (sector, multiplier, parents) in xTreeDepthFirst(originalSectorTree):
#    print sector, multiplier, parents
    sum += multiplier * sector.values[0]
print sum
sum = 0
for (sector, multiplier, parents) in xTreeDepthFirst(SectorTree):
#    print sector, multiplier, parents
    sum += multiplier * sector.values[0]
print sum
