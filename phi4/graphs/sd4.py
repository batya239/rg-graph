#!/usr/bin/python
# -*- coding: utf8
import copy
from comb import xUniqueCombinations
import conserv
from methods.feynman_tools import merge_grp_qi, conv_sub, qi_lambda, apply_eq, find_eq, dTau_line
from sd3 import FeynmanSubgraphs, gendet, apply_eq_onsub, check_cons, Domain, RequiredDecompositions

def decompose_vars(var_list):
    """
    generates list of subsectors for decomposition by vars in var_list
    """
    subsectors = []
    for var in var_list:
        _vars = copy.copy(var_list)
        _vars.remove(var)
        subsectors.append((var, _vars))
    return subsectors


class SectorTree:
    def __init__(self, pvar, svars, domains=list(), ds=dict(), parents=list(), primary=False):
        self.pvar = pvar
        self.svars = svars
        self.domains = domains
        self.parents = parents
        self.primary = primary
        self.ds = ds
        self.branches = list()
        self.__addbranches()
        self.strechs = list()


    def __addbranches(self):
        pvars = self.parents + [self.pvar]

        for domain in self.domains:
            vars_ = list(set(domain.vars) - set(pvars))
            vars = list()
            for var in vars_:
                if check_cons(pvars + [var], domain.cons):
                    vars.append(var)
            if len(vars) > 1:
                for subsect_vars in decompose_vars(vars):
                    pvar, svars = subsect_vars
                    #                    print pvars, vars, subsect_vars, domain
                    self.branches.append(SectorTree(pvar, svars, domains=copy.copy(self.domains), parents=pvars))

    def str(self):
        if self.primary:
            str_primary = "P"
        else:
            str_primary = ""

        if len(self.ds.keys()) == 0:
            str_ds = ""
        else:
            str_ds = str(self.ds)
        if len(self.strechs) == 0:
            str_strechs = ""
        else:
            str_strechs = str(tuple(self.strechs))
#        return "%s%s%s%s%s" % (self.pvar, str_primary, tuple(sorted(self.svars)), str_ds, str_strechs)
        return "%s%s%s%s" % (self.pvar, str_primary, tuple(sorted(self.svars)), str_ds)


def print_tree(sector_tree, parents=list()):
    if len(sector_tree.branches) == 0:
        print parents + [sector_tree.str()]
    else:
        for branch in sector_tree.branches:
        #            print sector_tree.pvar, sector_tree.svars, [x.str() for x in sector_tree.branches]
            print_tree(branch, parents + [sector_tree.str()])


def strech_list(sector, graph):
    """ generate list of strechs extracted in leading term by first pass of sector decomposition
    """

    strechs = []
    subs = graph._eqsubgraphs
    for j in range(len(subs)):
        si = len(set(sector) & set(subs[j])) - graph._subgraphs[j].NLoopSub()
        strechs += [1000 + j] * si
    return list(set(strechs))


def strechs_on_tree(sector_tree, graph):
    if len(sector_tree.branches) == 0:
        sector_tree.strechs = strech_list(sector_tree.parents + [sector_tree.pvar], graph)
#        print sector_tree.parents + [sector_tree.pvar], graph._eqsubgraphs
#        print sector_tree.strechs
        return sector_tree.strechs
    else:
        res = set()
        for branch in sector_tree.branches:
            res = res | set(strechs_on_tree(branch, graph))
        sector_tree.strechs = list(res)
        return sector_tree.strechs


def PrimaryTrees(graph, model):
    trees = list()
    for subsect_vars in decompose_vars(graph._qi.keys()):
        pvar, svars = subsect_vars
        trees.append(SectorTree(pvar, svars, primary=True, domains=[Domain(graph._qi.keys(), graph._cons, model)]))

    return trees


def SpeerTrees(graph, model):
    trees = PrimaryTrees(graph, model)
    for tree in trees:
        strechs_on_tree(tree, graph)
    return trees

def SplitDomains(domains, graph, subgraph_idx):
    new_domains = list()
    splitted = False
    subgraph_lines=graph._eqsubgraphs[subgraph_idx]
    for domain in domains:
        if subgraph_lines.issubset(set(domain.vars)):
            new_domains += list(domain.split(graph, subgraph_idx))
            splitted = True
        else:
            new_domains.append(domain)
    if not splitted:
        raise Exception, "Failed to split domain. domains: %s, subgraph: %s"%(self.domains, subgraph_lines)
    return new_domains

def FindStrechsForDS(sectortree, graph):
    res=list()
    subs = graph._eqsubgraphs
    sub_dims = graph._subgraph_dims
    strechs = sectortree.strechs
    sector = sectortree.parents+[sectortree.pvar]
    for strech in strechs:
        idx = strech - 1000
        if strech in sectortree.ds.keys():
            continue
        if len(set(subs[idx]) & set(sector)) >= RequiredDecompositions(sub_dims[idx]):
            sub=set(subs[idx])
            bad=False
            for strech2 in res:
                idx2=strech2-1000
                sub2=set(subs[idx2])
                if sub2.issubset(sub) or len(sub2&sub)==0:
                    bad=True
                    break
            if not bad:
                res.append(strech)
    return res

def ASectors(branches, graph, parent_ds=dict()):
    if len(branches) == 0:
        return
    else:
        new_branches = list()
        for branch in branches:
            branch.ds=copy.copy(parent_ds)
            strechs=FindStrechsForDS(branch, graph)
#            print "strechs = ",strechs, branch.parents+[branch.pvar], parent_ds
            for strech in strechs:
                idx = strech - 1000
                ds_ = copy.copy(parent_ds)
#                print "strech:",strech
#                print ds_
                for strech2 in strechs:
                    if strech2==strech:
                        ds_[strech2] = 0
                    else:
                        ds_[strech2] = 1
#                print ds_
                branch_=SectorTree(branch.pvar, branch.svars,ds=ds_,parents=branch.parents, domains=SplitDomains(branch.domains, graph, idx),primary=branch.primary )

                branch.ds=copy.copy(parent_ds)
                for strech2 in strechs:
                    branch.ds[strech2]=1
                new_branches.append(branch_)

        for tree in new_branches:
            strechs_on_tree(tree,graph)

        for branch in new_branches:
            branches.append(branch)
        for branch in branches:
            ASectors(branch.branches, graph, branch.ds)


def gensectors(graph, model):
    speer_trees = SpeerTrees(graph, model)
    ASectors(speer_trees,graph)
    return speer_trees

def gendet(graph):
    det=[]
    subs=graph._eqsubgraphs
    for i in xUniqueCombinations(graph._qi2l.keys(), graph.NLoops()):
        if check_cons(i, graph._cons):
            det.append(i+strech_list(i, graph))
    return det


def Prepare(graph, model):
    FeynmanSubgraphs(graph, model)

    int_edges = graph._internal_edges_dict()
    cons = conserv.Conservations(int_edges)
    eqs = find_eq(cons)

    cons = apply_eq(cons, eqs)

    print
    print "Conservations:\n", cons
    graph._cons = cons
    graph._qi, graph._qi2l = qi_lambda(cons, eqs)
    print graph._qi, graph._qi2l
    print "lines = ", graph.Lines()
    graph._eq_grp_orig = graph._eq_grp
    graph._eq_grp = merge_grp_qi(graph._eq_grp, graph._qi2l)

    ###debug
    #    g1 = dTau_line(graph, 5, model)
    #    FeynmanSubgraphs(g1, model)
    #    g1._eqsubgraphs = apply_eq_onsub(g1._qi2l, conv_sub(g1._subgraphs))
    ###debug
    #FeynmanSubgraphs(graph, model)
    graph._eqsubgraphs = apply_eq_onsub(graph._qi2l, conv_sub(graph._subgraphs))



    graph._subgraph_dims=[x.Dim(model) for x in graph._subgraphs]
#    graph._det = gendet(cons, graph._subgraphs, graph._qi, graph.NLoops()) #TODO rewrite
    graph._det = gendet(graph)
    print graph._det
    graph._sectors = gensectors(graph, model)

#    graph._sectors = gensectors(g1, model)
#    graph._det=gendet(cons, graph._subgraphs, graph._qi, graph.NLoops())
