#!/usr/bin/python
# -*- coding: utf8
import copy
import fnmatch

import itertools
import os
import re
import subprocess

import graph_state
import sys
import calculate

import graphs
import nodes
import conserv
from methods import sd_tools

from methods.feynman_tools import conv_sub
import polynomial
import subgraphs

import polynomial.sd_lib as sd_lib


class DynGraph(graphs.Graph):
    def __init__(self, arg):
        self._lines = list()
        self._nodes = list()
        if isinstance(arg, str):
            self._from_graphstate(graph_state.GraphState.fromStr(arg))
        elif isinstance(arg, graph_state.GraphState):
            self._from_graphstate(arg)
        else:
            raise NotImplementedError, "Unsupported type of argument : %s" % arg

    def _from_graphstate(self, gs):
        edges = gs.sortings[0]
        _nodes = dict()
        line_idx = 0
        for line in edges:
            for node_idx in line.nodes:
                if not _nodes.has_key(node_idx):
                #                    _type=None if node_idx>=0 else -1

                #FIXME: all nodes are of the same type
                    _type = 1 if node_idx >= 0 else -1
                    _nodes[node_idx] = nodes.Node(type=_type)
            self._lines.append(_nodes[line.nodes[0]].AddLine(_nodes[line.nodes[1]], type=line.fields.pair))
            self._lines[-1]._idx = line_idx
            line_idx += 1

        self._nodes = DynGraph.indexed_nodes(_nodes)

    @staticmethod
    def indexed_nodes(nodes_dict):
        res = list()
        for node_idx in nodes_dict.keys():
            node = nodes_dict[node_idx]
            node._idx = node_idx
            res.append(node)
        return res


def baseTRelations(graph):
    res = list()
    for line in graph._lines:
        if line.type == ('a', 'A'):
            res.append(tuple(map(lambda x: x.idx(), line.Nodes())))
        #        elif line.type == ('0','A'):
        #            res.append(line.Nodes())
        elif line.type == ('A', 'a'):
            res.append(tuple([x.idx() for x in reversed(line.Nodes())]))
    return res


def TRelations(graph):
    base = baseTRelations(graph)
    res = set(base)

    stop = False
    while not stop:
        tres = list()
        stop = True
        for trel1 in res:
            node = trel1[1]
            for trel2 in res:
                if trel2[0] == node and (trel1[0], trel2[1]) not in res:
                    tres.append((trel1[0], trel2[1]))
                    stop = False
        res = res | set(tres)
    res_ = dict()
    for node1, node2 in res:
        if not res_.has_key(node2):
            res_[node2] = list()
        res_[node2].append(node1)
    return res_


def TVersions(graph):
    trelations = TRelations(graph)
    nodes = [x.idx() for x in graph.xInternalNodes()]
    nnodes = len(nodes)
    res = list()
    for nodes_ in itertools.permutations(nodes):
        good = True
        for i in range(nnodes):
            node = nodes_[i]
            if node in trelations and len(set(nodes_[i:]) & set(trelations[node])) != 0:
                good = False
                break
        if good:
            res.append(nodes_)

    return res


def TCuts(graph, tVersion):
    res = list()
    for i in range(len(tVersion) - 1):
        tCut = list()
        left = set(tVersion[:i + 1])
        right = set(tVersion[i + 1:])
        for line in graph.xInternalLines():
            node1, node2 = map(lambda x: x.idx(), line.Nodes())
            if (node1 in left and node2 in right) or (node1 in right and node2 in left):
                tCut.append(line.idx())
        res.append(tCut)
    return res


def EffectiveSubgraphDim(subgraph, tCuts, model):
    sub = set([x.idx() for x in subgraph.lines])
    cnt = 0
    for tCut in tCuts:
        if len(sub & set(tCut)) <> 0:
            cnt += 1
    return subgraph.Dim(model) - model.freq_dim * (cnt - (len(subgraph.InternalNodes()) - 1) )


def genStatic_D_C(graph, model):
    internalEdges = graph._internal_edges_dict()
    if graph.Dim(model) == 2:
        internalEdges[1000000] = [i.idx() for i in graph.ExternalNodes()] #Additional edge: suitable way to find F
        conservations = conserv.Conservations(internalEdges)
        #        equations = sd_tools.find_eq(conservations)
        #        conservations = sd_tools.apply_eq(conservations, equations)
        equations = dict()
        graph._qi, graph._qi2l = sd_tools.qi_lambda(conservations, equations)
        graph._eqsubgraphs = sd_tools.apply_eq_onsub(graph._qi2l, conv_sub(graph._subgraphs))
        graph_ = graph.Clone()
        graph_._cons = conservations
        C = sd_tools.gendet(graph_, N=graph.NLoops() + 1)
        internalEdges = graph._internal_edges_dict()
        conservations = conserv.Conservations(internalEdges)
        #        conservations = sd_tools.apply_eq(conservations, equations)
        graph._cons = conservations

    else:
        C = [[], ]
        conservations = conserv.Conservations(internalEdges)
        #        equations = sd_tools.find_eq(conservations)
        equations = dict()
        #        conservations = sd_tools.apply_eq(conservations, equations)
        graph._qi, graph._qi2l = sd_tools.qi_lambda(conservations, equations)
        graph._eqsubgraphs = sd_tools.apply_eq_onsub(graph._qi2l, conv_sub(graph._subgraphs))
        graph._cons = conservations

    D = sd_tools.gendet(graph, N=graph.NLoops())
    return D, C


def relabel(lst, rules):
    res = list()
    for term in lst:
        term_ = list()
        for var in term:
            if rules.has_key(var):
                term_.append(rules[var])
            else:
                term_.append(var)
        res.append(term_)
    return res


def genStaticT(graph):
    res = list()
    for var in graph._qi2l:
        term = [var, ]
        for i in range(len(graph._subgraphs)):
            sub = map(lambda x: x.idx(), graph._subgraphs[i].lines)
            if var in sub:
                term.append('a%s' % i)
        res.append(term)
    return res


rules = {1000: 'a0', 1001: 'a1', 1002: 'a2', 1003: 'a3',
         1004: 'a4', 1005: 'a5', 1006: 'a6', 1007: 'a7',
         1008: 'a8', 1009: 'a9', 1010: 'a10'}

tCutShift = 100

def dSubstitutions(graph, tCuts):
    """
    TODO: generalization required
    """

    def isPhiPhi(line):
        return line.type == ('a', 'a')

    def isPhi1Phi(line):
        return line.type == ('A', 'a') or line.type == ('a', 'A')

    res = dict()
    for var in graph._qi2l:
        if len(graph._qi2l[var]) == 1:
            line = graph._Line(graph._qi2l[var][0])
        else:
            raise NotImplementedError, "all lines must have different Feynman parameters: %s" % graph._qi2l
        res[var] = list()

        if isPhiPhi(line):
            res[var].append((var,))
        for idx in range(len(tCuts)):
            tCut = tCuts[idx]

            if var in tCut:
                tsubst = [idx + tCutShift, ]
                for i in range(len(graph._subgraphs)):
                    sub = graph._subgraphs[i]
                    sub_ = set(map(lambda x: x.idx(), sub.lines))
                    if len(set(tCut) & sub_) <> 0 and var not in sub_:
                        tsubst.append('a%s' % i)
                res[var].append(tsubst)
    return res


def generateStaticCDET(dG, model):
    D, C = map(lambda x: relabel(x, rules), genStatic_D_C(dG, model))
    E = [(x,) for x in dG._qi2l]
    T = genStaticT(dG)
    return C, D, E, T


def tCutsInRange(tVersion, externalNodesIdx):
    res = list()
    inRange = False
    for idx in range(len(tVersion)):
        node = tVersion[idx]
        if not inRange:
            if node in externalNodesIdx:
                inRange = True
        else:
            res.append(idx - 1)
            if node in externalNodesIdx:
                inRange = False
                break
    return res


def dOmega(graph, tCuts, tCutsOmega):
    res = list()
    for idx in tCutsOmega:
        term = list()
        tCut = tCuts[idx]
        term.append(idx + tCutShift)
        for i in range(len(graph._subgraphs)):
            sub = graph._subgraphs[i]
            sub_ = set(map(lambda x: x.idx(), sub.lines))
            if len(set(tCut) & sub_) != 0:
                term.append('a%s' % i)
        res.append(term)
    return res




def generateCDET(dG, tVersion, staticCDET=None, model=None):
    if staticCDET is None:
        (C, D, E, T) = generateStaticCDET(dG, model)
    else:
        (C, D, E, T) = staticCDET

    tCuts = TCuts(dG, tVersion)
    Components = (C, D, E, T)
    Components_ = map(lambda y: polynomial.poly([(1, x) for x in y]), Components)

    substitutions = dSubstitutions(dG, tCuts)

    externalLinesType = map(lambda x: x.type, dG.ExternalLines())
    if externalLinesType == [('0', 'A'), ('0', 'a')] or externalLinesType == [('0', 'a'), ('0', 'A')]:
        externalNodes = dG.ExternalNodes()
        externalNodesIdx = map(lambda x: x.idx(), externalNodes)
        print tVersion, tCuts, externalNodes
        tCutsOmega = tCutsInRange(tVersion, externalNodesIdx)
        print tCutsOmega

        Components_[3] = Components_[3] * polynomial.poly([(1, x) for x in dOmega(dG, tCuts, tCutsOmega)])

    print "Substitutions:"
    for var in substitutions:
        subs = substitutions[var]
        print var, subs
        subs_ = polynomial.poly([(1, x) for x in subs])
        Components_ = map(lambda x: x.changeVarToPolynomial(var, subs_), Components_)
    print

    #d=4-2*e
    nLoops = dG.NLoops()
    #reduce(lambda x, y: x + y, [(-x.Dim(model) - 2) / 2 for x in dG.xInternalLines()]) - number of (a,a) edges (dim(a,a) = -4, dim(a,A)=-2)
    alpha = reduce(lambda x, y: x + y, [(-x.Dim(model) - 2) / 2 for x in dG.xInternalLines()]) + 1 + len(tCuts)
    print alpha

    if dG.Dim(model) == 0:
        Components_[0] = polynomial.poly([(1, [])])  # C
        Components_[1] = Components_[1].changeDegree((-model.space_dim / 2., 1))  # D
        Components_[2] = Components_[2].changeDegree((-alpha + model.space_dim * nLoops / 2., -nLoops))  # E
    elif dG.Dim(model) == 2:
        if externalLinesType == [('0', 'A'), ('0', 'a')] or externalLinesType == [('0', 'a'), ('0', 'A')]:
            Components_[0] = polynomial.poly([(1, [])])  # C
            Components_[1] = Components_[1].changeDegree((-model.space_dim / 2., 1))  # D
            Components_[2] = Components_[2].changeDegree((-alpha + model.space_dim * nLoops / 2. - 1, -nLoops))  # E
        else:
            Components_[1] = Components_[1].changeDegree((-model.space_dim / 2 - 1., 1))  # D
            Components_[2] = Components_[2].changeDegree((-alpha + model.space_dim * nLoops / 2. - 1, -nLoops))  # E

    return tuple(Components_)


def to1(a):
    def wrapper(expr):
        expr_ = expr
        if not isinstance(expr, list):
            expr_ = [expr, ]
        return map(lambda x: x.set1toVar(a), expr_)

    return wrapper


def mK_(exprList, a, n):
    res = list()
    currList = exprList

    if n >= 0:
        currList = map(lambda x: -x, currList)
        res += map(lambda x: x.set0toVar(a), currList)
    else:
        raise ValueError, "negative n: n=%s" % n
    aMultiplier = polynomial.poly([(1, [])])
    for i in xrange(1, n + 1):
        currList_ = list()
        aMultiplier *= polynomial.poly([(1. / i, ())])
        for expr in currList:
            currList_ += expr.diff(a)
        currList = currList_
        res += map(lambda x: x.set0toVar(a) * aMultiplier, currList)
    return res


def mK0(a):
    def wrapper(exprList):
        expr_ = exprList
        if not isinstance(exprList, list):
            expr_ = [exprList, ]

        return mK_(expr_, a, 0)

    return wrapper


def mK1(a):
    def wrapper(exprList):
        expr_ = exprList
        if not isinstance(exprList, list):
            expr_ = [exprList, ]

        return mK_(expr_, a, 1)

    return wrapper


def mK2(a):
    def wrapper(exprList):
        expr_ = exprList
        if not isinstance(exprList, list):
            expr_ = [exprList, ]

        return mK_(expr_, a, 2)

    return wrapper


def diff_(exprList, a, n):
    aMultiplier = polynomial.poly([(1, []), (-1, [a, ])], degree=(n - 1, 0)).toPolyProd()
    res = exprList
    #    print " 1 ", res

    for i in range(n):
        res_ = list()
        for expr in res:
            if not expr.isZero():
                res_ += expr.diff(a)
        res = res_
        #    print " ", res

    if n > 1:
        res = map(lambda x: x * aMultiplier, res)

    #    print " ", res
    return res


def D1(a):
    def wrapper(exprList):
        expr_ = exprList
        if not isinstance(exprList, list):
            expr_ = [exprList, ]

        return diff_(expr_, a, 1)

    return wrapper


def D2(a):
    def wrapper(exprList):
        expr_ = exprList
        if not isinstance(exprList, list):
            expr_ = [exprList, ]

        return diff_(expr_, a, 2)

    return wrapper


def D2s(a):
    def wrapper(exprList):
        expr_ = exprList
        if not isinstance(exprList, list):
            expr_ = [exprList, ]

        diffA = diff_(expr_, a, 1)
        return diffA + map(lambda x: -x.set0toVar(a), diffA)

    return wrapper


def D3(a):
    def wrapper(exprList):
        expr_ = exprList
        if not isinstance(exprList, list):
            expr_ = [exprList, ]

        return diff_(expr_, a, 3)

    return wrapper

#############################################
# sectors
#############################################


class Tree(object):
    def __init__(self, node):
        self.node = node
        self.branches = list()

    def setBranches(self, branches):
        self.branches = list()
        for branch in branches:
            if isinstance(branch, Tree):
                self.branches.append(branch)
            else:
                self.branches.append(Tree(branch))

    def addSector(self, sector):
        currentDecomposition = sector[0]
        tail = sector[1:]
        primaryVar = currentDecomposition[0]
        secondaryVars = currentDecomposition[1]
        decompositionSpace = [primaryVar] + list(secondaryVars)
        branchNodes = dict(map(lambda x: (x.node, x), self.branches))
        branchesToAdd = list()
        if primaryVar in branchNodes:
            nextBranch = branchNodes[primaryVar]
        for var in decompositionSpace:
            if var in branchNodes:
                continue
            else:
                if var == primaryVar:
                    nextBranch = Tree(primaryVar)
                    branchesToAdd.append(nextBranch)
                else:
                    branchesToAdd.append(var)
        self.setBranches(self.branches + branchesToAdd)
        if len(tail) > 0:
            nextBranch.addSector(tail)





def xTreeElement(tree, parents=list()):
    parents_ = copy.copy(parents)
    if tree.node is not None:
        parents_.append(tree.node)
    if len(tree.branches) == 0:
        yield parents_
    else:
        for branch in tree.branches:
            for elem in xTreeElement(branch, parents_):
                yield elem


def xTreeElement2(tree, parents=list(), varMap=dict(), debug=False):
    if len(tree.branches) == 0:
        yield parents
    else:
        branchIds = [x if x not in varMap else varMap[x] for x in map(lambda x: x.node, tree.branches)]
        for branch in tree.branches:
            branchIds_ = copy.copy(branchIds)
            branchIds_.remove(branch.node)
            parents_ = copy.copy(parents) + [(branch.node if branch.node not in varMap else varMap[branch.node],
                                              branchIds_)]
            for elem in xTreeElement2(branch, parents_, varMap):
                yield elem
            if tree.node is None and debug:
                print
        if debug:
            print


def validVar(var, parentsSet, conservations):
    if var in parentsSet:
        return False
    else:
        primaryVars = parentsSet | set([var])
        for cons in conservations:
            if cons.issubset(primaryVars):
                return False
        return True


def addBranches(tree, variables, conservations, parents=list(), depth=0):
    if depth == 0:
        return
    else:
        if len(tree.branches) == 0:
            parentsSet = set(parents) | set([tree.node])
            branches = list()
            for var in variables:
                if validVar(var, parentsSet, conservations):
                    branches.append(var)
            if len(branches) == 1:
                raise ValueError, branches
            elif len(branches) != 0:

                tree.setBranches(branches)
            for branch in tree.branches:
                if tree.node is None:
                    parents_ = parents
                else:
                    parents_ = parents + [tree.node]
                if not isinstance(tree.node, int):
                    depthDecrement = 0
                else:
                    depthDecrement = 1
                addBranches(branch, variables, conservations, parents=parents_, depth=depth - depthDecrement)
        else:
            for branch in tree.branches:
                if tree.node is None:
                    parents_ = parents
                else:
                    parents_ = parents + [tree.node]
                if not isinstance(tree.node, int):
                    depthDecrement = 0
                else:
                    depthDecrement = 1
                addBranches(branch, variables, conservations, parents=parents_, depth=depth - depthDecrement)


def det2treeSubstitutions(substitutions, branchVars):
    res = dict()
#    print "det2treeSubstitutions", branchVars
    for var in substitutions:
        subs = substitutions[var]
        newSubs = list()
#        print var, subs
        for term in subs:
            newTerm = list()
#            print "term  ",     term
            for item in term:
                skip = False
                if isinstance(item, int):
                    candidate = item
                else:
                    if item in branchVars:
                        skip = True
            if not skip:
                newTerm.append(candidate)
            if len(newTerm) <= 1:
                newSubs += newTerm
            else:
                raise ValueError, newTerm

        res[var] = newSubs
    return res


def transformTree(tree, substitutions):
    if len(tree.branches) == 0:
        return
    else:
        newBranches = list()
        branchVars = map(lambda x: x.node, tree.branches)
#        print "transformTree",  substitutions
#        print
        treeSubstitutions = det2treeSubstitutions(substitutions, branchVars)
        for branch in tree.branches:
            if isinstance(branch.node, str):
                transformTree(branch, substitutions)
                newBranches.append(branch)
            else:
                for var in treeSubstitutions[branch.node]:
                    branch_ = copy.deepcopy(branch)
                    branch_.node = var
                    transformTree(branch_, substitutions)
                    newBranches.append(branch_)
        tree.setBranches(newBranches)


def removeBranchesWithParents(tree, parents=set()):
    if len(tree.branches) == 0:
        return
    else:
        newBranches = list()
        for branch in tree.branches:
            if branch.node not in parents:
                newBranches.append(branch)
                parents_ = copy.copy(parents) | set([branch.node])
                removeBranchesWithParents(branch, parents_)
                tree.setBranches(newBranches)


def findShortBranches(tree, parents=set(), depth=None):
    if len(tree.branches) == 0:
        return
    else:
        branchIds = map(lambda x: x.node, tree.branches)
        parents_ = copy.copy(parents)
        if tree.node is not None:
            parents_ = parents_ | set([tree.node])
        for parent in parents_:
            if branchIds.count(parent) > depth:
                tree.branches = list()
                break
        if not isinstance(tree.node, int):
            depthDecrement = 0
        else:
            depthDecrement = 1
        for branch in tree.branches:
            findShortBranches(branch, parents_, depth=depth - depthDecrement)


def joinDuplicates(tree):
    if len(tree.branches) == 0:
        return
    else:
        branchMap = dict()
        for branch in tree.branches:
            if branch.node not in branchMap:
                branchMap[branch.node] = branch
            else:
                if len(branchMap[branch.node].branches) == 0 or len(branch.branches) == 0:
                    branchMap[branch.node].branches = list()
                else:
                    branchMap[branch.node].branches += branch.branches
        tree.setBranches(branchMap.values())
        for branch in tree.branches:
            joinDuplicates(branch)


def generateStaticSpeerTree(variables, conservations, nLoops, tree=None):
    if tree is None:
        staticSpeerTree = Tree(None)
    else:
        staticSpeerTree = tree
    addBranches(staticSpeerTree, variables, conservations, depth=nLoops)
    return staticSpeerTree


def generateDynamicSpeerTree(dG, tVersion, model, tree=None):
    if "_subgraphs" not in dG.__dict__:
        dG.FindSubgraphs(model)
        subgraphs.RemoveTadpoles(dG)

    if '_cons' not in dG.__dict__:
        genStatic_D_C(dG)

    tCuts = TCuts(dG, tVersion)
    substitutions = dSubstitutions(dG, tCuts)
#    treeSubstitutions = det2treeSubstitutions(substitutions)

    variables = dG._qi.keys()
    conservations = dG._cons
    nLoops = dG.NLoops()
    # for sector in xTreeElement2(tree):
    #     print  "    (%s, (  ))," % (sector)

    if tree is None:
        speerTree = generateStaticSpeerTree(variables, conservations, nLoops)
    else:
        speerTree = generateStaticSpeerTree(variables, conservations, nLoops, tree=tree)

    # for sector in xTreeElement2(speerTree):
    #     print  "    (%s, (  ))," % (sector)
    # print
    #
    # print substitutions
    # print

    transformTree(speerTree, substitutions)
    # for sector in xTreeElement2(speerTree):
    #     print  "    (%s, (  ))," % (sector)
    # print


    findShortBranches(speerTree, depth=nLoops)
    removeBranchesWithParents(speerTree)
    joinDuplicates(speerTree)
    return speerTree


def checkDecomposition_(expr):
    exprStatus = "bad"
    if len(expr.polynomials) == 0:
        return "0"
    for poly in expr.polynomials:

        if poly.degree.a < 0:
            if len(poly.monomials) > 1:
                polyStatus = "bad"
                for monomial in poly.monomials.keys():
                    if len(monomial) == 0:
                        polyStatus = "1"
                        break
                    else:
                        if reduce(lambda x, y: x & y, [isinstance(x, str) for x in monomial.vars]):
                            polyStatus = "%s" % monomial
                if polyStatus == "bad":
                    exprStatus = "bad"
                    break
                elif polyStatus == "1":
                    if exprStatus == "1" or exprStatus == "bad":
                        exprStatus = "1"
                else:
                    if exprStatus == "1" or exprStatus == "bad":
                        exprStatus = polyStatus
                    else:
                        exprStatus = exprStatus + " " + polyStatus
            elif not poly.isConst():
                exprStatus = 'pole'
    return exprStatus


def checkDecomposition(exprList):
    exprList_ = exprList
    if not isinstance(exprList, list):
        exprList_ = [exprList, ]

    checks = map(checkDecomposition_, exprList_)
    return checks


#####################################
# save expr
#####################################

def splitUA(varSet):
    u = list()
    a = list()
    for var in varSet:
        if isinstance(var, str) and re.match('^a.*', var):
            a.append(var)
        else:
            u.append(var)
    return set(u), set(a)


def deltaArg(varSet):
    return polynomial.poly(map(lambda x: (1, [x]), varSet))


resultingFunctionPvTemplate = """
double func_t_{fileIdx}(double k[DIMENSION])
{{
double f=0;
{resultingFunctions}
return f;
}}
"""

functionPvTemplate = """
double func{idx}_t_{fileIdx}(double k[DIMENSION])
{{
// sector {sector}
{vars}
double coreExpr;
double f=0;
{expr}
return f;
}}
"""

functionsPvCodeTeplate = """
#include <math.h>
#include "dim.h"

{functions}

{resultingFunction}
"""

headerPvCodeTeplate = """
#include <math.h>
#include "dim.h"

double func_t_{idx}(double k[DIMENSION]);
"""

dimPvCodeTemplate = """
#define DIMENSION {dims}
"""


def saveSectors(sectorTerms, name, dirname, fileIdx, neps, introduce=False):
    sectorFunctionsByEps = [""] * (neps + 1)
    resultingFunctions = ""
    for idx in sectorTerms:
        sectorExpr, sectorVariables = sectorTerms[idx]

        strVars = ""
        varIdx = 0
        for var in sectorVariables:
            strVars += "   double %s = k[%s];\n" % (var, varIdx)
            varIdx += 1

        strExpr = [""] * (neps + 1)
        if not introduce:
            for expr_ in sectorExpr:
                if not expr_.isZero():
                    coreExpr, epsDict = expr_.epsExpansion(neps)
                    coreExprString = polynomial.formatter.format(coreExpr, polynomial.formatter.CPP)
                    for i in xrange(neps + 1):
                        epsTerms = epsDict[i]
                        strExpr[i] += "   coreExpr = %s;\n" % coreExprString
                        for epsTerm in epsTerms:
                            strExpr[i] += "   f += coreExpr * %s;\n" % (
                                polynomial.formatter.format(epsTerm, polynomial.formatter.CPP))
        else:
            epsExp = dict([(i, []) for i in range(neps + 1)])
            for expr_ in sectorExpr:
                if not expr_.isZero():
                    coreExpr, epsDict = expr_.epsExpansion(neps)
                    for i in range(neps+1):
                        epsExp[i].append((coreExpr, epsDict[i]))
            for i in range(neps+1):
                exprTuples, substDict = polynomial.formatter.formatPairsWithExtractingNewVariables(epsExp[i], exportType=polynomial.formatter.CPP)
                for var in substDict:
                    strExpr[i] += "   double %s = %s;\n" % (var, substDict[var])
                for coreExpr, epsTerms in exprTuples:
                    epsTermsSting = ""
                    for epsTerm in epsTerms:
                        epsTermsSting += "+ (%s)" % epsTerm
                    if len(epsTermsSting)>0:
                        epsTermsSting = epsTermsSting[1:]
                    strExpr[i] += "   f += (%s)*(%s);\n" % (coreExpr, epsTermsSting)



        for i in range(neps + 1):
            sectorFunctionsByEps[i] += functionPvTemplate.format(idx=idx, fileIdx=fileIdx,
                                                                 sector=idx, vars=strVars,
                                                                 expr=strExpr[i])
        resultingFunctions += "f+=func{idx}_t_{fileIdx}(k);\n".format(idx=idx, fileIdx=fileIdx)
    resultingFunction = resultingFunctionPvTemplate.format(fileIdx=fileIdx,
                                                           resultingFunctions=resultingFunctions)
    for i in range(neps + 1):
        f = open("%s/%s_func_%s_E%s.c" % (dirname, name, fileIdx, i), 'w')
        f.write(functionsPvCodeTeplate.format(resultingFunction=resultingFunction,
                                              functions=sectorFunctionsByEps[i]))
        f.close()
        f = open("%s/%s_func_%s_E%s.h" % (dirname, name, fileIdx, i), 'w')
        f.write(headerPvCodeTeplate.format(idx=fileIdx))
        f.close()


def saveSectorsSDT(sectorTerms, name, dirname, fileIdx, neps):
#    print "sectorTerms"
    sectorFunctionsByEps = [""] * (neps + 1)
    resultingFunctions = ""
    for idx in sectorTerms:
        sectorExpr, sectorVariables, primaryVar, substNumerator, substDenominator = sectorTerms[idx]

        strVars = ""
        varIdx = 0
        for var in sectorVariables:
            strVars += "   double %s = k[%s];\n" % (var, varIdx)
            varIdx += 1
        substNumeratorString = polynomial.formatter.format(substNumerator, polynomial.formatter.CPP)
        substDenominatorString = polynomial.formatter.format(substDenominator, polynomial.formatter.CPP)
        strVars += "   if( 1 - (%s) -(%s) > 0) { return 0.; } \n" % (substNumeratorString, substDenominatorString)
        strVars += "   if( 1 - (%s)  < 0) { return 0.; } \n" % (substNumeratorString)
        primaryVarStr = polynomial.formatter.format(primaryVar, polynomial.formatter.CPP)

        strVars += "   double %s = (1. - (%s))/(%s);\n" % (primaryVarStr, substNumeratorString, substDenominatorString)

        strExpr = [""] * (neps + 1)
        for expr_ in sectorExpr:
            if not expr_.isZero():
                coreExpr, epsDict = expr_.epsExpansion(neps)
                coreExprString = polynomial.formatter.format(coreExpr, polynomial.formatter.CPP)
                for i in xrange(neps + 1):
                    epsTerms = epsDict[i]
                    strExpr[i] += "   coreExpr = (%s) / (%s);\n" % (coreExprString, substDenominatorString)
                    for epsTerm in epsTerms:
                        strExpr[i] += "   f += coreExpr * (%s);\n" % (
                            polynomial.formatter.format(epsTerm, polynomial.formatter.CPP))
        for i in range(neps + 1):
            sectorFunctionsByEps[i] += functionPvTemplate.format(idx=idx, fileIdx=fileIdx,
                                                                 sector=idx, vars=strVars,
                                                                 expr=strExpr[i])
        resultingFunctions += "f+=func{idx}_t_{fileIdx}(k);\n".format(idx=idx, fileIdx=fileIdx)
    resultingFunction = resultingFunctionPvTemplate.format(fileIdx=fileIdx,
                                                           resultingFunctions=resultingFunctions)
    for i in range(neps + 1):
        f = open("%s/%s_func_%s_E%s.c" % (dirname, name, fileIdx, i), 'w')
        f.write(functionsPvCodeTeplate.format(resultingFunction=resultingFunction,
                                              functions=sectorFunctionsByEps[i]))
        f.close()
        f = open("%s/%s_func_%s_E%s.h" % (dirname, name, fileIdx, i), 'w')
        f.write(headerPvCodeTeplate.format(idx=fileIdx))
        f.close()


corePvCodeTemplate = """
#include <math.h>
#include <stdio.h>
#include <vegas.h>
#include <stdlib.h>
#include <time.h>
#include "dim.h"
#define gamma tgamma
#define FUNCTIONS 1
#define ITERATIONS 5
#define NTHREADS 2
#define NEPS 0
#define NITER 2

{includes}

double reg_initial[2*DIMENSION]={hypercube};

void func (double k[DIMENSION], double f[FUNCTIONS])
 {{
  f[0]=0.;
  {functions}
 }}



int t_gfsr_k;
unsigned int t_gfsr_m[SR_P];
double gfsr_norm;


int main(int argc, char **argv)
{{
  int i;
  long long npoints;
  int nthreads;
  int niter;
  double region_delta;
  double reg[2*DIMENSION];
  int idx;
  if(argc >= 2)
    {{
      npoints = atoll(argv[1]);

    }}
  else
    {{
      npoints = ITERATIONS;
    }}

  if(argc >= 3)
    {{
      nthreads = atoi(argv[2]);

    }}
  else
    {{
      nthreads = NTHREADS;
    }}

   if(argc >= 5)
    {{
      region_delta = atof(argv[4]);

    }}
  else
    {{
      region_delta = 0.;
    }}

  if(argc >= 4)
    {{
      niter = atoi(argv[3]);

    }}
  else
    {{
      niter = NITER;
    }}

    for(idx=0; idx<2*DIMENSION; idx++)
      {{
         if(idx<DIMENSION)
           {{
             reg[idx] = reg_initial[idx]+region_delta;
           }}
         else
           {{
             reg[idx] = reg_initial[idx]-region_delta;
           }}
      }}

  double estim[FUNCTIONS];   /* estimators for integrals                     */
  double std_dev[FUNCTIONS]; /* standard deviations                          */
  double chi2a[FUNCTIONS];   /* chi^2/n                                      */
    clock_t start, end;
    double elapsed;
    start = clock();

{mpiInit}

  vegas(reg, DIMENSION, func,
        0, npoints/10, 5, NPRN_INPUT | NPRN_RESULT,
        FUNCTIONS, 0, nthreads,
        estim, std_dev, chi2a);
  vegas(reg, DIMENSION, func,
        2, npoints , niter, NPRN_INPUT | NPRN_RESULT,
        FUNCTIONS, 0, nthreads,
        estim, std_dev, chi2a);
    int rank=0;

{mpiFinalize}

    if(rank==0) {{
        end = clock();
        elapsed = ((double) (end - start)) / CLOCKS_PER_SEC;
        double delta= std_dev[0]/estim[0];
        printf ("result = %20.18g\\nstd_dev = %20.18g\\ndelta = %20.18g\\ntime = %20.10g\\n", estim[0], std_dev[0], delta, elapsed);
    }}
    return(0);
}}
"""


def core_pv_code(nFunctionFiles, sectorVariablesCount, functionName, neps, mpi=False):
    includes = ""
    functions = ""
    for i in range(nFunctionFiles):
        functions += "\n f[0] += func_t_%s(k);\n" % i
        includes += "#include \"%s_%s_E%s.h\"\n" % (functionName, i, neps)

    if mpi:
        includes += "#include <mpi.h>\n"

    if mpi:
        mpiInit = "\nMPI_Init(&argv, &argc);\n"
        mpiFinalize = "\nMPI_Comm_rank(MPI_COMM_WORLD,&rank);\nMPI_Finalize();\n"
    else:
        mpiInit = ""
        mpiFinalize = ""
    hyperCube = '{' + ",".join(['0', ] * sectorVariablesCount) + "," + ",".join(['1', ] * sectorVariablesCount) + "}"

    return corePvCodeTemplate.format(
        includes=includes,
        mpiInit=mpiInit,
        mpiFinalize=mpiFinalize,
        hypercube=hyperCube,
        functions=functions)


def core_pvmpi_code(nFunctionFiles, sectorVariablesCount, functionName, neps):
    return core_pv_code(nFunctionFiles, sectorVariablesCount, functionName, neps, mpi=True)


code_ = core_pv_code

method_name = "simpleSD"


def removeRoots(expr):
    res = list()
    for expr_ in expr:
        uVars, aVars = splitUA(expr_.getVarsIndexes())
        tExpr = expr_
        for var in uVars:
            tExpr = tExpr.changeVarToPolynomial(var,
                                                polynomial.poly([(1, [var, var])], c=1, degree=1)) * polynomial.poly(
                [(1, [var])], c=2.)
        res.append(tExpr.simplify())
    return res


def save(model, expr, sectors, name, neps, statics=False, introduce=False):
    dirname = '%s/%s/%s/' % (model.workdir, method_name, name)
    try:
        os.mkdir('%s/%s' % (model.workdir, method_name))
    except:
        pass
    try:
        os.mkdir(dirname)
    except:
        pass

    if statics:
        name_ = name + "_O_"
    else:
        name_ = name

    variables = expr.getVarsIndexes()
    uVars, aVars = splitUA(variables)
    delta_arg = deltaArg(uVars)

    maxSize = 30000
    sectorCount = -1
    size = 0
    nSaved = 0
    fileIdx = 0

    sectorTerms = dict()
    sectorVariablesCount = 0
    if "subtractionOperators" in model.__dict__:
        exec model.subtractionOperators
    for item in sectors:
        if len(item) == 2:
            sector, aOps = item
            coef = 1.
        elif len(item) == 3:
            sector, aOps, coef = item
        else:
            raise NotImplementedError, "len(sector)>3"
        coef_ = polynomial.poly([(1, [])], c=coef)
        sectorCount += 1
        if (sectorCount + 1) % 100 == 0:
            print "%s " % (sectorCount + 1)

        #        print delta_arg, sector

        sectorExpr = sd_lib.sectorDiagram(expr * coef_, sector, delta_arg=delta_arg)[0]
        for aOp_ in aOps:
            print aOp_
            aOp = eval(aOp_)
            sectorExpr = aOp(sectorExpr)


        sectorExpr = map(lambda x: x.simplify(), sectorExpr)

        if 'removeRoots' in model.__dict__ and model.removeRoots:
            sectorExpr = removeRoots(sectorExpr)

        check = checkDecomposition(sectorExpr)
        if len(check) == 0:
            continue
        if not reduce(lambda x, y: x & y, map(lambda x: "0" == x or "1" == x, check)):
            print
            print sector, check
            print polynomial.formatter.format(sectorExpr, polynomial.formatter.CPP)
            print

        sectorVariables = set()
        for expr_ in sectorExpr:
            sectorVariables = sectorVariables | set(polynomial.formatter.formatVarIndexes(expr_,
                                                                                          polynomial.formatter.CPP))
        if len(sectorVariables) > sectorVariablesCount:
            sectorVariablesCount = len(sectorVariables)

        sectorTerms[sectorCount] = (sectorExpr, sectorVariables)
        #    toSave = dict()
        #    for sectorId in sectorTerms:
        #        toSave[sectorId] = sectorTerms[sectorId]
        size += sectorTerms[sectorCount].__sizeof__()

        if size >= maxSize:
            saveSectors(sectorTerms, name_, dirname, fileIdx, neps, introduce=introduce)
            fileIdx += 1
            nSaved += len(sectorTerms)
            print "saved to file  %s sectors (%s) size=%s..." % (nSaved, fileIdx, size)
            sys.stdout.flush()
            sectorTerms = dict()
            size = 0
    if size > 0:
        saveSectors(sectorTerms, name_, dirname, fileIdx, neps, introduce=introduce)
        fileIdx += 1
        nSaved += len(sectorTerms)
        print "saved to file  %s sectors (%s) size=%s..." % (nSaved, fileIdx, size)
        sys.stdout.flush()

    for i in range(neps + 1):
        f = open("%s/%s_E%s.c" % (dirname, name_, i), 'w')
        f.write(code_(fileIdx, sectorVariablesCount, "%s_func" % name_, neps=i))
        f.close()
        f = open("%s/dim.h" % dirname, 'w')
        f.write(dimPvCodeTemplate.format(dims=sectorVariablesCount))
        f.close()


# def splitDeltaArg(delta_arg_):
#     delta_arg = delta_arg_.toPolyProd().simplify()
#     if len(delta_arg.polynomials) != 2:
#         raise ValueError("invalid delta_arg decomposition: %s" % delta_arg)
#     if len(delta_arg.polynomials[0].monomials) == 1:
#         return delta_arg.polynomials[0], 1, delta_arg.polynomials[1]
#     elif len(delta_arg.polynomials[1].monomials) == 1:
#         return delta_arg.polynomials[1], 1, delta_arg.polynomials[0]

def hasConst(polynomial):
    for mi in polynomial.monomials:
        if len(mi) == 0:
            return True
    return False


def splitDeltaArg(delta_arg_):
    variables = delta_arg_.getVarsIndexes()
    nTerms = len(delta_arg_.monomials)
#    print "delta_arg", delta_arg_
    for var in variables:
        numerator = delta_arg_.set0toVar(var)
#        print "numerator", numerator, nTerms - len(numerator.monomials) >1, "var ", var
        if nTerms - len(numerator.monomials) > 1:
            denominator = delta_arg_.toPolyProd().diff(var)
#            print "denominator", denominator
            if len(denominator) > 1:
                continue
            if len(denominator[0].polynomials) > 1:
                continue
            if len(denominator[0].polynomials[0].monomials) != len(denominator[0].polynomials[0].set0toVar(var).monomials):
                continue

#            if hasConst(denominator[0].polynomials[0]):
##                print "res", var, numerator.toPolyProd(), denominator[0]
#                return var, numerator.toPolyProd(), denominator[0]
            return var, numerator.toPolyProd(), denominator[0]
    raise ValueError("can't remove delta function %s" % delta_arg_)


def saveSDT(model, expr, sectors, name, neps, statics=False):
    dirname = '%s/%s/%s/' % (model.workdir, method_name, name)
    try:
        os.mkdir('%s/%s' % (model.workdir, method_name))
    except:
        pass
    try:
        os.mkdir(dirname)
    except:
        pass

    if statics:
        name_ = name + "_O_"
    else:
        name_ = name

    variables = expr.getVarsIndexes()
    uVars, aVars = splitUA(variables)
    delta_arg = deltaArg(uVars)

    maxSize = 30000
    sectorCount = -1
    size = 0
    nSaved = 0
    fileIdx = 0

    sectorTerms = dict()
    sectorVariablesCount = 0

    for item in sectors:
        if len(item) == 2:
            sector, aOps = item
            coef = 1.
        elif len(item) == 3:
            sector, aOps, coef = item
        else:
            raise NotImplementedError, "len(sector)>3"
        coef_ = polynomial.poly([(1, [])], c=coef)
        sectorCount += 1
        if (sectorCount + 1) % 100 == 0:
            print "%s " % (sectorCount + 1)

        #        print delta_arg, sector
        sectorExpr = [expr * coef_, ]

        for aOp_ in aOps:
            aOp = eval(aOp_)
            sectorExpr = aOp(sectorExpr)

#        sectorExpr_, delta_arg_sd_ = sd_lib.sectorDiagram(sectorExpr, sector[:1], delta_arg=delta_arg, remove_delta=False)

        sectorExpr, delta_arg_sd = sd_lib.sectorDiagram(sectorExpr, sector, delta_arg=delta_arg, remove_delta=False)
        # sectorExpr_ = list()
        # for expr_ in sectorExpr:
        #     sectorExpr_.append(sd_lib.sectorDiagram(expr_, sector, remove_delta=False))
        # #        sectorExpr = reduce(lambda x, y: x + y, map(
        # #            lambda x: sd_lib.sectorDiagram(x, sector, remove_delta=False), sectorExpr))
        # delta_arg_sd = sd_lib.sectorDiagram(delta_arg.toPolyProd(), sector, remove_delta=False)
        # sectorExpr = sectorExpr_
        sectorExpr = map(lambda x: x.simplify(), sectorExpr)
#        print sector
#        print delta_arg_sd
        primaryVar, substNumerator, substDenominator = splitDeltaArg(delta_arg_sd)

        if 'removeRoots' in model.__dict__ and model.removeRoots:
            sectorExpr = removeRoots(sectorExpr)

        # check = checkDecomposition(sectorExpr)
        # #        print sector, check
        # if "bad" in check:
        #     print
        #     print sector
        #     print polynomial.formatter.format(sectorExpr, polynomial.formatter.CPP)
        #     print check
        #     print

        sectorVariables = set()
        for expr_ in sectorExpr:
            sectorVariables = sectorVariables | set(polynomial.formatter.formatVarIndexes(expr_,
                                                                                          polynomial.formatter.CPP))
        sectorVariables = sectorVariables - set([polynomial.formatter.format(primaryVar, polynomial.formatter.CPP)])

        if len(sectorVariables) > sectorVariablesCount:
            sectorVariablesCount = len(sectorVariables)

        sectorTerms[sectorCount] = (sectorExpr, sectorVariables, primaryVar, substNumerator, substDenominator)
        #    toSave = dict()
        #    for sectorId in sectorTerms:
        #        toSave[sectorId] = sectorTerms[sectorId]
        size += sectorTerms[sectorCount].__sizeof__()

        if size >= maxSize:
            saveSectorsSDT(sectorTerms, name_, dirname, fileIdx, neps)
            fileIdx += 1
            nSaved += len(sectorTerms)
            print "saved to file  %s sectors (%s) size=%s..." % (nSaved, fileIdx, size)
            sys.stdout.flush()
            sectorTerms = dict()
            size = 0
    if size > 0:
        saveSectorsSDT(sectorTerms, name_, dirname, fileIdx, neps)
        fileIdx += 1
        nSaved += len(sectorTerms)
        print "saved to file  %s sectors (%s) size=%s..." % (nSaved, fileIdx, size)
        sys.stdout.flush()

    for i in range(neps + 1):
        f = open("%s/%s_E%s.c" % (dirname, name_, i), 'w')
        f.write(code_(fileIdx, sectorVariablesCount, "%s_func" % name_, neps=i))
        f.close()
        f = open("%s/dim.h" % dirname, 'w')
        f.write(dimPvCodeTemplate.format(dims=sectorVariablesCount))
        f.close()


def compileCode(model, name, options=list(), cc="gcc", statics=False):
#TODO: rewrite
    dirname = '%s/%s/%s/' % (model.workdir, method_name, name)
    os.chdir(dirname)
    if statics:
        name_ = name + "_O_"
    else:
        name_ = name

    obj_list = dict()
    failed = False
    for file in os.listdir("."):
        if fnmatch.fnmatch(file, "*__func_*.c"):
            regex = re.match('.*_func_\d+_E(\d+)\.c', file)
            if regex:
                eps_num = int(regex.groups()[0])
                if eps_num not in obj_list.keys():
                    obj_list[eps_num] = list()
                obj_list[eps_num].append(file)
            print "Compiling objects %s ..." % file,
            sys.stdout.flush()
            obj_name = file[:-2] + ".o"
            try:
                os.remove(obj_name)
            except:
                pass
            process = subprocess.Popen([cc, file] + options + ["-c"] + ["-o", obj_name], shell=False,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            exit_code = process.wait()
            (std_out, std_err) = process.communicate()
            if exit_code <> 0:
                print "FAILED"
                print std_err
                failed = True
            else:
                if len(std_err) == 0:
                    print "OK"
                else:
                    print "CHECK"
                    print std_err
            sys.stdout.flush()
    print

    for file in os.listdir("."):
        if fnmatch.fnmatch(file, "*.c") and not fnmatch.fnmatch(file, "*__func_*.c"):
            regex = re.match('(.*)_E(\d+)\.c', file)
            if regex:
                code_name = regex.groups()[0]
                eps_num = int(regex.groups()[1])
                #            print code_name

            print "Compiling %s ..." % file,
            sys.stdout.flush()
            prog_name = file[:-2] + "_.run"
            try:
                os.remove(prog_name)
            except:
                pass
            obj_ = list()
            #            print
            for obj__ in obj_list[eps_num]:
                if re.match('^%s.*' % code_name, obj__):
                #                    print code_name,  obj__[:-2]+".o"
                    obj_.append(obj__[:-2] + ".o")
                    #            print
                    #            print obj_
                    #            print [cc, file] + options + ["-I", ".", "-L", "."] + obj_ + ["-o", prog_name]
            process = subprocess.Popen(
                [cc, file] + options + ["-I", ".", "-L", "."] + obj_ + ["-o", prog_name], shell=False,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            exit_code = process.wait()
            (std_out, std_err) = process.communicate()
            if exit_code <> 0:
                print "FAILED"
                print std_err
                failed = True
            else:
                if len(std_err) == 0:
                    print "OK"
                else:
                    print "CHECK"
                    print std_err
            sys.stdout.flush()
    return not failed


def execute(name, model, points=10000, threads=4, calc_delta=0., neps=0):
    #method_name = "simpleSD"
    return calculate.execute("%s/%s/" % (method_name, name), model, points=points, threads=threads,
                             calc_delta=calc_delta, neps=neps)


def Replace(fileName):
    symbolsToReplace = '-:(),'
    res = fileName
    for symbol in symbolsToReplace:
        res = res.replace(symbol, "_")
    res = res.replace(' ', "")
    return res
