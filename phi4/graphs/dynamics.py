#!/usr/bin/python
# -*- coding: utf8
import copy

import itertools

import graph_state

import graphs
import nodes
import conserv
from methods import sd_tools

from methods.feynman_tools import conv_sub
import polynomial
import subgraphs


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


def TCuts(graph, tversion):
    res = list()
    for i in range(len(tversion) - 1):
        tcut = list()
        left = set(tversion[:i + 1])
        right = set(tversion[i + 1:])
        for line in graph.xInternalLines():
            node1, node2 = map(lambda x: x.idx(), line.Nodes())
            if (node1 in left and node2 in right) or (node1 in right and node2 in left):
                tcut.append(line.idx())
        res.append(tcut)
    return res


def EffectiveSubgraphDim(subgraph, tCuts, model):
    sub = set([x.idx() for x in subgraph.lines])
    cnt = 0
    for tCut in tCuts:
        if len(sub & set(tCut)) <> 0:
            cnt += 1
    return subgraph.Dim(model) - model.freq_dim * (cnt - (len(subgraph.InternalNodes()) - 1) )


def genStatic_D_C(graph):
    internalEdges = graph._internal_edges_dict()
    if len(graph.ExternalLines()) == 2:
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
        conservation = conserv.Conservations(internalEdges)
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


rules = {1000: 'a0', 1001: 'a1', 1002: 'a2', 1003: 'a3', 1004: 'a4', 1005: 'a5', 1006: 'a6', 1007: 'a7'}


def dSubstitutions(graph, tCuts):
    """
    TODO: generalization required
    """

    def isPhiPhi(line):
        return line.type == ('a', 'a')

    def isPhi1Phi(line):
        return line.type == ('A', 'a') or line.type == ('a', 'A')

    tCutShift = 100

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


def generateStaticCDET(dG):
    D, C = map(lambda x: relabel(x, rules), genStatic_D_C(dG))
    E = [(x,) for x in dG._qi2l]
    T = genStaticT(dG)
    return C, D, E, T


def generateCDET(dG, tVersion, staticCDET=None, model=None):
    if staticCDET is None:
        (C, D, E, T) = generateStaticCDET(dG)
    else:
        (C, D, E, T) = staticCDET

    tCuts = TCuts(dG, tVersion)
    Components = (C, D, E, T)
    Components_ = map(lambda y: polynomial.poly([(1, x) for x in y]), Components)

    substitutions = dSubstitutions(dG, tCuts)
    for var in substitutions:
        subs = substitutions[var]
        subs_ = polynomial.poly([(1, x) for x in subs])
        Components_ = map(lambda x: x.changeVarToPolynomial(var, subs_), Components_)

    #d=4-2*e
    nLoops = dG.NLoops()
    alpha = len([x for x in dG.xInternalLines()])

    if dG.Dim(model) == 0:
        Components_[0] = polynomial.poly([(1, [])])  # C
        Components_[1].degree.a, Components_[1].degree.b = (-model.space_dim / 2., 1)  # D
        Components_[2].degree.a, Components_[2].degree.b = (-alpha + model.space_dim * nLoops / 2., nLoops)  # E
    elif dG.Dim(model) == 2:
        Components_[1].degree.a, Components_[1].degree.b = (-model.space_dim / 2 - 1., 1)  # D
        Components_[2].degree.a, Components_[2].degree.b = (-alpha + model.space_dim * nLoops / 2. - 1, nLoops)  # E

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
        aMultiplier *= polynomial.poly([(1. / i, (a,))])
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
                addBranches(branch, variables, conservations, parents=parents_, depth=depth - 1)


def det2treeSubstitutions(substitutions):
    res = dict()
    for var in substitutions:
        subs = substitutions[var]
        newSubs = list()
        for term in subs:
            newTerm = list()
            for item in term:
                if isinstance(item, int):
                    newTerm.append(item)
            if len(newTerm) == 1:
                newSubs += newTerm
            else:
                raise ValueError, newTerm

        res[var] = newSubs
    return res


def transformTree(tree, treeSubstitutions):
    if len(tree.branches) == 0:
        return
    else:
        newBranches = list()
        for branch in tree.branches:
            for var in treeSubstitutions[branch.node]:
                branch_ = copy.deepcopy(branch)
                branch_.node = var
                transformTree(branch_, treeSubstitutions)
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

        for branch in tree.branches:
            findShortBranches(branch, parents_, depth=depth - 1)


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


def generateStaticSpeerTree(variables, conservations, nLoops):
    staticSpeerTree = Tree(None)
    addBranches(staticSpeerTree, variables, conservations, depth=nLoops)
    return staticSpeerTree


def generateDynamicSpeerTree(dG, tVersion, model):
    if "_subgraphs" not in dG.__dict__:
        dG.FindSubgraphs(model)
        subgraphs.RemoveTadpoles(dG)

    if '_cons' not in dG.__dict__:
        genStatic_D_C(dG)

    tCuts = TCuts(dG, tVersion)
    substitutions = dSubstitutions(dG, tCuts)
    treeSubstitutions = det2treeSubstitutions(substitutions)

    variables = dG._qi.keys()
    conservations = dG._cons
    nLoops = dG.NLoops()
    speerTree = generateStaticSpeerTree(variables, conservations, nLoops)

    transformTree(speerTree, treeSubstitutions)

    findShortBranches(speerTree, depth=nLoops)
    removeBranchesWithParents(speerTree)
    joinDuplicates(speerTree)
    return speerTree


def checkDecomposition_(expr):
    exprStatus = "bad"
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
            #                print expr
            #                print poly

    return exprStatus


def checkDecomposition(exprList):
    exprList_ = exprList
    if not isinstance(exprList, list):
        exprList_ = [exprList, ]

    checks = map(checkDecomposition_, exprList_)
    return checks
