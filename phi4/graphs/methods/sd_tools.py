#!/usr/bin/python
# -*- coding: utf8
import copy
import fnmatch
import os
import re
import subprocess
import sympy
import comb
import conserv
from methods.feynman_tools import find_eq, apply_eq, qi_lambda, conv_sub, merge_grp_qi, strech_indexes
from methods.poly_tools import poly_exp, set1_poly_lst, minus, set0_poly_lst, diff_poly_lst, poly_list2ccode, factorize_poly_lst, exp_pow, poly2str

try:
    import DiagramAlgo
    _DiagramAlgo=True
except:
    _DiagramAlgo=False

#_DiagramAlgo=False

import subgraphs

class SubSector:
    def __init__(self, primary_var, secondary_vars, primary=False, ds_vars=None, coef=1.):
        self.pvar = primary_var

        self.svars = sorted(secondary_vars)
        self.primary = primary
        self.coef=coef
        if ds_vars == None:
            self.ds = {}
        else:
            self.ds = ds_vars

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.primary:
            primary = 'P'
        else:
            primary = ''
        if len(self.ds.keys()) == 0:
            ds = ""
        else:
            ds = str(self.ds)

        return "%s%s%s%s" % (self.pvar, primary, tuple(self.svars), ds)


class Sector:
    def __init__(self, sect_list):
        """
        sector (sec_list -> list of SubSectors),
        coef - coefficient of this sector (symmetries)
        """
        self.subsectors = copy.deepcopy(sect_list)
        self.ds = {}
        coef=1.
        for subsector in self.subsectors:
            if 'coef' in dir(subsector):
                coef=coef*subsector.coef
        self.coef = coef
        self._UpdateDS()
        self.domains = []
        self.excluded_vars = list()

    def __len__(self):
        return len(self.subsectors)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "coef=%s,%s"%(self.coef, self.subsectors)

    def append(self, subsector):
        """
        remove?
        """
        self.subsectors.append(subsector)
        self._UpdateDS()

    def __add__(self, other):
        if isinstance(other, Sector):
            if other.coef <> 1:
                raise ValueError, "invalid value of .coef for %s" % other
            S = Sector(self.subsectors + other.subsectors)
            S.domains=copy.deepcopy(self.domains)
            return S
        elif isinstance(other, SubSector):
            S = Sector(self.subsectors + [other], coef=self.coef)
            S.domains=copy.deepcopy(self.domains)
            return S
        else:
            raise TypeError, "cant perform addition of decomposition and %s" % type(other)
    def __hash__(self):
        return str(self).__hash__()


    def __eq__(self, other):
        return str(self)==str(other)

    def cut(self, level):
        S=Sector(copy.deepcopy(self.subsectors[:level]), coef=self.coef)
        S.domains=copy.deepcopy(self.domains)
        return S

    def PrimaryVars(self):
        """
        Returns primary decomposition vars for sector
        """
        res = []
        for subsector in self.subsectors:
            res.append(subsector.pvar)
        return res

    def SetDS(self, level, var, value):
        self.subsectors[level].ds[var] = value
        self._UpdateDS()

    def _UpdateDS(self):
        self.ds = dict()
        for subsector in self.subsectors:
            for var in subsector.ds:
                if var in self.ds:
                    raise ValueError, " %s already in ds : %s; sector: %s" % (var, self.ds, self)
                self.ds[var] = subsector.ds[var]

    def SplitDomain(self, graph, subgraph_idx):
        new_domains = list()
        splitted = False
        subgraph_lines=graph._eqsubgraphs[subgraph_idx]
        for domain in self.domains:
            if subgraph_lines.issubset(set(domain.vars)):
                new_domains += list(domain.split(graph, subgraph_idx))
                splitted = True
            else:
                new_domains.append(domain)
        if not splitted:
            raise Exception, "Failed to split domain. domains: %s, subgraph: %s"%(self.domains, subgraph_lines)
        self.domains = new_domains


class Domain:
    def __init__(self, vars, conservations, model):
        self.vars = vars
        self.cons = conservations
        self.model = model

    def __repr__(self):
#        return str(self.vars) +" (" + str(self.cons) + ") "
        return str(self.vars)

    def split(self, graph, subgraph_lines):
        """
        split domain
        """
        if not set(subgraph_lines).issubset(set(self.vars)):
            raise ValueError, "Cant split domain %s using subgraph %s"%(self.vars, subgraph_lines)
        vars1=list(set(subgraph_lines) & set(self.vars))
        vars2=list(set(self.vars) - set(subgraph_lines))
        cons1=set([])
        cons2=set([])
        for cons_ in self.cons:
            cons__=frozenset(set(cons_)&set(vars1))
            if len(cons__)>0:
                cons1 = cons1 | set([cons__])
            else:
                cons2 = cons2 | set([cons_])
#        print vars1, subgraph.Dim(self.model), subgraph.NLoopSub()
##        for cons_ in comb.xUniqueCombinations(vars1, subgraph.Dim(self.model)):
#        for cons_ in comb.xUniqueCombinations(vars1, subgraph.NLoopSub()):
#            print "2", cons2
#            cons2 = cons2 | set([frozenset(cons_)])
#        print "cons1 ", cons1
#        print "cons2 ", cons2
        return (Domain(vars1, cons1, self.model), Domain(vars2, cons2, self.model))

def check_cons(term, cons):
    """
    check if the combination of vars denied by conservation laws
    """
    res = True
    for constr in cons:
#        print term, constr, constr.issubset(term)
        if constr.issubset(term):
            res = False
            break
    return res

def RequiredDecompositions(degree):
    """
    How much decompositions required for subgraph with UVdegree=degree to be able to perform direct subtractions
    """
    if degree == 0:
        return 1
    elif degree == 2:
        return 2
    else:
        raise NotImplementedError, "Direct subtractions not available for graphs with degree=%s" % degree

def SplitDomains(domains, graph, subgraph_idx=None, subgraph=None):
    new_domains = list()
    splitted = False
    if subgraph_idx<>None and subgraph<>None:
        raise ValueError, "subgraph_idx and subgraph are set at the same time"
    if subgraph_idx<>None:
        subgraph_lines=graph._eqsubgraphs[subgraph_idx]
    if subgraph<>None:
        subgraph_lines=subgraph
    for domain in domains:
        if subgraph_lines.issubset(set(domain.vars)):
            new_domains += list(domain.split(graph, subgraph_lines))
            splitted = True
        else:
            new_domains.append(domain)
    if not splitted:
        raise Exception, "Failed to split domain. domains: %s, subgraph: %s"%(domains, subgraph_lines)
    return new_domains

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

def xTreeElement(sector_tree, parents=list(), coef=1):
    """
    Iterate over sector tree
    """

    if len(sector_tree.branches) == 0:
        parents_=parents + [SubSector(sector_tree.pvar,sector_tree.svars,primary=sector_tree.primary, ds_vars=sector_tree.ds, coef=coef*sector_tree.coef)]
        yield parents_
    else:
        for branch in sector_tree.branches:
            parents_=parents + [SubSector(sector_tree.pvar,sector_tree.svars,primary=sector_tree.primary)]
            for term in xTreeElement(branch, parents_, coef*sector_tree.coef):
                yield term

class SectorTree:
    def __init__(self, pvar, svars, domains=list(), ds=dict(), parents=list(), primary=False, coef=1):
        self.pvar = pvar
        self.svars = svars
        self.domains = domains
        self.parents = parents
        self.primary = primary
        self.ds = ds
        self.branches = list()
        self.__addbranches()
        self.strechs = list()
        self.coef = coef


    def __addbranches(self):
        pvars = self.parents + [self.pvar]
#        print
#        print "addbranches ", pvars, self.domains
        for domain in self.domains:
#            print domain, domain.cons
            vars_ = list(set(domain.vars) - set(pvars))
#            print vars_
            vars = list()
            for var in vars_:
                if check_cons(pvars + [var], domain.cons):
                    vars.append(var)
#            print vars
            if len(vars) > 1:
                for subsect_vars in decompose_vars(vars):
                    pvar, svars = subsect_vars
                    self.branches.append(SectorTree(pvar, svars, domains=copy.copy(self.domains), parents=pvars))
                if len(self.branches)>0:
                    break

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
        return "(%s)%s%s%s%s %s" % (self.coef,self.pvar, str_primary, tuple(sorted(self.svars)), str_ds, str_strechs)
#        return "(%s)%s%s%s%s" % (self.coef,self.pvar, str_primary, tuple(sorted(self.svars)), str_ds)


def print_tree(sector_tree, parents=list()):
    if len(sector_tree.branches) == 0:
        print parents + [sector_tree.str()], sector_tree.domains
    else:
        for branch in sector_tree.branches:
            print_tree(branch, parents + [sector_tree.str()])


def FeynmanSubgraphs(graph, model):
    """
    Find subgraphs required for Feynman representation
    """
    model.SetTypes(graph)
    model.checktadpoles = False
    graph.FindSubgraphs(model)

    subs_toremove = subgraphs.DetectSauseges(graph._subgraphs)
    graph.RemoveSubgaphs(subs_toremove)

    subgraphs.RemoveTadpoles(graph)

def apply_eq_onsub(qi2l, subgraphs_as_set):
    """
    Apply equations on subgraphs (ex. if lines 4 and 5 have the same qi=4, subgraph [4,5,6,7], becomes [4,6,7])
    now I'm not sure that this is necessary
    """
    reverse_qi = dict()
    for var in qi2l:
        for v_ in qi2l[var]:
            reverse_qi[v_] = var
        reverse_qi[var] = var

    res = list()
    for sub in subgraphs_as_set:
        sub_ = set([])
        for v in sub:
            sub_ = sub_|set([reverse_qi[v]])
        res.append(sub_)
    return res

def strech_list(sector, graph):
    """ generate list of strechs extracted in leading term by first pass of sector decomposition
    """

    strechs = []
    subs = graph._eqsubgraphs
    for j in range(len(subs)):
        si = len(set(sector) & set(subs[j])) - graph._subgraphs[j].NLoopSub()
#        print subs[j], sector, si
        strechs += [1000 + j] * si
    return list(set(strechs))

def PrimaryTrees(graph, model):
    trees = list()
    for subsect_vars in decompose_vars(graph._qi.keys()):
        pvar, svars = subsect_vars
        trees.append(SectorTree(pvar, svars, primary=True, domains=[Domain(graph._qi.keys(), graph._cons, model)]))



    return trees

def strechs_on_tree(sector_tree, graph):
    """
    label nodes with strechs on sub tree
    """
    if len(sector_tree.branches) == 0:
#        print "strechs_on_tree"
#        print sector_tree.parents + [sector_tree.pvar]
        sector_tree.strechs = strech_list(sector_tree.parents + [sector_tree.pvar], graph)
#        print sector_tree.strechs
        return sector_tree.strechs
    else:
        res = set()
        for branch in sector_tree.branches:
            res = res | set(strechs_on_tree(branch, graph))
        sector_tree.strechs = list(res)
        return sector_tree.strechs

def ColouredLines(lines_dict, colouredlines):
    _lines_dict=copy.deepcopy(lines_dict)
    for line in lines_dict:
        _lines_dict[line].append(0)
    for i in range(len(colouredlines)):
        _lines_dict[colouredlines[i]][2]=(i+1)
    return _lines_dict


def RemoveEquivalentSpeerSectors(branches, lines_dict, coef=1):
    """
    Remove equivalent speer sectors
    """

    if len(branches) == 0:
        return branches
    else:

        equiv_sectors = dict()
        nomenkl_sector = dict()
        for branch in branches:
            CL = ColouredLines(lines_dict,branch.parents+[branch.pvar])
#            print "CL=", CL
            cnomenkl = DiagramAlgo.NickelLabel(CL)
            if cnomenkl not in equiv_sectors.keys():
                equiv_sectors[cnomenkl]=1
                nomenkl_sector[cnomenkl]=branch
            else:
                equiv_sectors[cnomenkl]+=1
        _branches=list()
        for cnomenkl in nomenkl_sector:
            branch=nomenkl_sector[cnomenkl]
            branch_factor = equiv_sectors[cnomenkl]

            branch.coef = branch_factor
            branch.branches=RemoveEquivalentSpeerSectors(branch.branches, lines_dict, coef=branch.coef)
            _branches.append(branch)
        return _branches



def SpeerTrees(graph, model):
    """
    Generate Speer sectors for graph, then label nodes with strechs on sub tree
    """
    trees = PrimaryTrees(graph, model)
    t_=[]
    for tree in trees:
        t_+=[x for x in xTreeElement(tree)]
    print "speer_sectors:",len(t_)
    for tree in trees:
        strechs_on_tree(tree, graph)
#        print_tree(tree)
    if _DiagramAlgo:
        trees = RemoveEquivalentSpeerSectors(trees, graph._edges_dict())
    return trees


def gensectors(graph, model):
    """
    generate sectors for graph (speer sectors, then branches for DS terms with a=0
    """
    speer_trees = SpeerTrees(graph, model)
    t_=list()
    for tree in speer_trees:
        t_+=[x for x in xTreeElement(tree)]
#        print_tree(tree)
    print "speer_sectors symm:",len(t_)

    ASectors(speer_trees,graph)
    return speer_trees

def gendet(graph, N=None):
    """
    generate deynman det for graph
    """
    if N==None:
        N_=graph.NLoops()
    else:
        N_=N
    det=[]
    for i in comb.xUniqueCombinations(graph._qi2l.keys(), N_):
        if check_cons(i, graph._cons):
            det.append(i+strech_list(i, graph))
    return det

def RequiredDecompositionSum(graph, ds, idx):
    res=0
    subs=graph._eqsubgraphs
#    print "ds=",ds
    for idx_ in range(len(graph._eqsubgraphs)):
#           print idx_, idx_+1000 in ds.keys() and  ds[idx_+1000]==0
        if idx_+1000 in ds.keys() and ds[idx_+1000]==0:
#            print  subs[idx_].issubset(subs[idx])
            if idx<>idx_ and subs[idx_].issubset(subs[idx]):
                res+=RequiredDecompositions(graph._subgraph_dims[idx_])
    res+=RequiredDecompositions(graph._subgraph_dims[idx])
    return res



def FindStrechsForDS(sectortree, graph):
    res=list()
    subs = graph._eqsubgraphs
    sub_dims = graph._subgraph_dims
    strechs = sectortree.strechs
    sector = sectortree.parents+[sectortree.pvar]
    sector_set=set(sector)
#    print
#    print "FindStrechsForDS", sector, sectortree.ds, "a_strechs ",strechs, subs
    MinNloop=None
    for idx in range(len(subs)):
#    for strech in strechs:

        strech = idx + 1000
#        print strech, sector_set, sectortree.ds, subs[idx], sector_set-subs[idx]
        if strech in sectortree.ds.keys():
            if sectortree.ds[strech]==0:
                sector_set=sector_set-subs[idx]
            continue
        if strech not in strechs:
            continue
#        if len(set(subs[idx]) & set(sector)) >= RequiredDecompositions(sub_dims[idx]):
#        print sectortree.ds
#        print strech, set(subs[idx]) & set(sector_set), RequiredDecompositions(sub_dims[idx]), MinNloop, graph._subgraphs[idx].NLoopSub()
        if MinNloop==None and len(set(subs[idx]) & set(sector_set))>0:
            MinNloop=graph._subgraphs[idx].NLoopSub()
        if MinNloop==graph._subgraphs[idx].NLoopSub() and (len(set(subs[idx]) & set(sector_set)) >= RequiredDecompositions(sub_dims[idx])):
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

def FindOverlapingSubgraphsIdx(eqsubgraphs,subgraph_idx):
    sub=eqsubgraphs[subgraph_idx]
    res=list()
    for i in range(len(eqsubgraphs)):
        intersect= eqsubgraphs[i]&sub
        if len(intersect)>0 and intersect<>sub and intersect<>eqsubgraphs[i]:
            res.append(i)
    return res


def ASectors(branches, graph, parent_ds=dict()):
    """
    generate branches for ds terms with a=0
    """
    if len(branches) == 0:
        return
    else:
#        print
        new_branches = list()
        subs = graph._eqsubgraphs
        for branch in branches:
            branch.ds=copy.copy(parent_ds)

#            if len(branch.branches)>0:
#                strechs=FindStrechsForDS(branch, graph)
#            else:
#                continue

            strechs=FindStrechsForDS(branch, graph)
#            print branch.parents,  branch.pvar, branch.ds, "a_strechs", branch.strechs, "strechs", strechs, "domains", branch.domains

            for strech in strechs:
                idx = strech - 1000
                ds_ = copy.copy(parent_ds)
                _subgraph=copy.copy(subs[idx])
                for strech3 in ds_:
                    idx_=strech3-1000
                    if ds_[strech3]==0:
#                        if subs[idx_].issubset(_subgraph):
                        if subs[idx_].issubset(subs[idx]):
                            _subgraph=_subgraph-subs[idx_]

                for strech2 in strechs:
                    if strech2==strech:
                        ds_[strech2] = 0
                    else:
                        ds_[strech2] = 1
#                print "overlap", FindOverlapingSubgraphsIdx(subs, idx)
                for idx2 in FindOverlapingSubgraphsIdx(subs, idx):
                    if idx2+1000 not in ds_:
                        ds_[idx2+1000] = 1

                branch_=SectorTree(branch.pvar, branch.svars,ds=ds_,parents=branch.parents,
                    domains=SplitDomains(branch.domains, graph, subgraph=_subgraph),primary=branch.primary, coef=branch.coef )
#                print "child: ", branch_.parents,  branch_.pvar, branch_.ds, "a_strechs", branch_.strechs
#                strechs_on_tree(branch_,graph)
#                print "child: ", branch_.parents,  branch_.pvar, branch_.ds, "a_strechs", branch_.strechs
#                print branch_.str(), branch_.domains
#                print_tree(branch_)
#                print
                branch.ds=copy.copy(parent_ds)
                for strech2 in strechs:
                    branch.ds[strech2]=1
                new_branches.append(branch_)

        for tree in new_branches:
            strechs_on_tree(tree,graph)
#            print_tree(tree)

        for branch in new_branches:
            branches.append(branch)
        for branch in branches:
            ASectors(branch.branches, graph, branch.ds)


def Prepare(graph, model):
    FeynmanSubgraphs(graph, model)

    int_edges = graph._internal_edges_dict()
    if len(graph.ExternalLines())==2:
        int_edges[1000000]=[i.idx() for i in graph.ExternalNodes()]
    cons = conserv.Conservations(int_edges)
    eqs = find_eq(cons)
    cons = apply_eq(cons, eqs)
    graph._qi, graph._qi2l = qi_lambda(cons, eqs)
    graph._eqsubgraphs = apply_eq_onsub(graph._qi2l, conv_sub(graph._subgraphs))
    print graph._qi, graph._qi2l
    if len(graph.ExternalLines())==2:
        graph_=graph.Clone()
        graph_._cons=cons
        Cdet = gendet(graph_, N=graph.NLoops()+1)
        print "Cdet terms:",len(Cdet)
#        print "Cdet= ",Cdet
    else:
        Cdet = None

    graph._cdet = Cdet



    int_edges = graph._internal_edges_dict()
    cons = conserv.Conservations(int_edges)
    #    print "Conservations:\n", cons
    #    graph._cons = cons
    #    eqs = find_eq(cons)
    cons = apply_eq(cons, eqs)
    #    print
    print "Conservations:\n", cons, eqs
    graph._cons = cons

    print "lines = ", graph.Lines()
    graph._eq_grp_orig = graph._eq_grp
    graph._eq_grp = merge_grp_qi(graph._eq_grp, graph._qi2l)

    graph._subgraph_dims=[x.Dim(model) for x in graph._subgraphs]

    graph._det = gendet(graph)
    print "Det terms:",len(graph._det)
    #print "det=",graph._det
    sub_idx=-1
    for sub in graph._subgraphs:
        sub_idx+=1
        sub._strechvar=1000+sub_idx
        print "%s sub = %s"%(sub._strechvar,  sub)
        
    graph._sectors = gensectors(graph, model)
    t_=0
    for tree in graph._sectors:
        t_+=len([x for x in xTreeElement(tree)])
#        print
#        print_tree(tree)
    print "A_sectors: ",t_


def jakob_poly(sector):
    """
    term from jakobian
    """
    res = list()
    for subsector in sector.subsectors:
        res+=[subsector.pvar]*len(subsector.svars)
        if subsector.primary:
            res+=[subsector.pvar]
    return res

def diff_subtraction(term,  strechs, sector):
    """ perform diff subtraction for ALL strechs that wasn't affected by direct_subtraction
    """
    res=[term]
    for var in strechs:
        if var in sector.excluded_vars:
            continue
        terms_=[]
        if strechs[var]==0:
            for term_ in res:
                terms_.append(set1_poly_lst(term_, var))
        elif strechs[var]==1:
            for term_ in res:
                terms_+=diff_poly_lst(term_, var)
        elif strechs[var]==2:
            for term_ in res:
                firstD=diff_poly_lst(term_, var)
                for term_ in firstD:
                    seconD=diff_poly_lst(term_, var)
                    for term__ in seconD:
                    ##не работает если переменная имеет индекс 0
                        term__.append(poly_exp([[], [-var]], (1, 0)))
                        terms_+=[term__]
        else:
            raise NotImplementedError,  "strech level   = %s"%strechs[var]
        res=terms_
    return res

def decompose_expr(sector,poly_lst, strechs, jakob=True):
    jakobian=jakob_poly(sector)
    res = copy.copy(poly_lst)
    for subsector in sector.subsectors:
        res_n = list()
        for poly in res:
            res_n.append(poly.strech(subsector.pvar,subsector.svars))
        res = res_n

    if jakob:
        res.append(poly_exp([jakobian],(1,0), coef=(1,0)))
    terms=[res]
#    print terms
#    print strechs
    for strech in strechs:
        sidx=strech
        terms_n=[]
#        print strech, strechs[strech], sector.ds
        if strechs[strech]==0:
            if not sidx in sector.ds.keys() or sector.ds[sidx]==1:
                """
                strech set to 1 or doesn't require subtraction
                drop sectors with subtractions (else)
                """
                for term in terms:
                    terms_n.append(set1_poly_lst(term, strech))
                sector.excluded_vars.append(strech)
            else:
                terms=[]
                break
        elif  strechs[strech]==1 and sidx in sector.ds.keys():
            if sector.ds[sidx]==0:
                for term in terms:
                    terms_n.append(minus(set0_poly_lst(term,strech)))
            else:
                for term in terms:
#                    print "1  ", term
#                    print "11 ", set1_poly_lst(term,strech)
                    terms_n.append(set1_poly_lst(term,strech))

            sector.excluded_vars.append(strech)
        elif  strechs[strech]==2 and (sidx in sector.ds.keys()) :
            if sector.ds[sidx]==0:
                for term in terms:
                    terms_n.append(minus(set0_poly_lst(term,strech)))
                    firstD=diff_poly_lst(term, strech)
                    for term_ in firstD:
                        terms_n.append(minus(set0_poly_lst(term_,strech)))
            else:
                for term in terms:
                    terms_n.append(set1_poly_lst(term,strech))
            sector.excluded_vars.append(strech)
        else:
            terms_n=terms
        terms=terms_n
#        print terms

    return terms

def save_sectors(g1, sector_terms, strech_vars, name_, idx, neps=0):

    sect_terms=[dict() for i in range(neps+1)]
    for sector in sector_terms.keys():

        subs=[[x] for x in g1._qi.keys()]
        subs.remove([sector.subsectors[0].pvar])

        subs_polyl = decompose_expr(Sector(sector.subsectors[1:]), [poly_exp(subs,  (1, 0))], list() , jakob=False)
        if len(subs_polyl)<>1:
            raise Exception, "invalid decomposition for delta function term"

        terms = sector_terms[sector]
        tres = ["",]*(neps+1)
        e,D = sympy.var('e D')
        D_ = None
        D_present = [False,]*(neps+1)
        for i in range(len(terms)):
            term = terms[i]
            if len(term)==0:
                continue
            (leading, eps_poly, log_func, log_pow) = extract_eps(term)
            if D_==None:
                D_ = poly2str(log_func)
            else:
                if D_<>poly2str(log_func):
                    raise Exception, "Determinants are different: \n%s\n%s "%(D_,poly2str(log_func))

            f_term = poly_list2ccode(factorize_poly_lst(leading))
            for j in range(neps+1):
                eps_term_= (eps_poly*(sympy.exp(log_pow*e*sympy.log(D)))).diff(e,j).subs(e,0)/sympy.factorial(j)
                if D in eps_term_.atoms():
                    D_present[j] = True
                eps_term = sympy.printing.ccode((eps_term_).evalf())
                tres[j]+="(%s)*(%s);\nres+="%(f_term, eps_term)
        for j in range(neps+1):
            if D_present[j]:
                sect_terms[j][sector] = (tres[j][:-5], poly_list2ccode(subs_polyl[0]),D_)
            else:
                sect_terms[j][sector] = (tres[j][:-5], poly_list2ccode(subs_polyl[0]),"0.")
    for j in range(neps+1):
        f=open("%s_func_%s_E%s.c"%(name_,idx, j),'w')
        f.write(code_f(functions(sect_terms[j], g1._qi.keys(), strech_vars, idx), len(g1._qi.keys())+len(strech_vars)))
        f.close()
        f=open("%s_func_%s_E%s.h"%(name_,idx, j),'w')
        f.write(code_h( idx, len(g1._qi.keys())+len(strech_vars)))
        f.close()

def code_f(func,N):
    res="""
#include <math.h>
#define DIMENSION %s
"""%(N-1)
    res+=func
    return res

def code_h(idx, N):
    res="""
#include <math.h>
#define DIMENSION %s
double func_t_%s(double k[DIMENSION]);

"""%(N-1, idx)

    return res



def functions(poly_dict, vars,  strechs,  index=None):
    if index==None:
        sindex=""
    else:
        sindex="_t_%s"%index
    res2="""
double func%s(double k[DIMENSION])
{
double f=0.;
"""%sindex
    cnt=0
    res=""
    varstring=""
    varstring2=""
    for i in range(len(vars)+len(strechs)-1):
        varstring+="double w_%s,"%i
        varstring2+="k[%s],"%i
    varstring=varstring[:-1]
    varstring2=varstring2[:-1]
    for sector in poly_dict.keys():
        res+="""
double func%s_%s( %s)
{
//sector %s
"""%(cnt,index, varstring,sector)
        cnt2=0

        s0="1./(1.+"
        for var in vars+strechs:
            if var<>sector.subsectors[0].pvar:
                res+="double u%s=w_%s;\n"%(var,cnt2)
                cnt2+=1



        expr, subs, D_=poly_dict[sector]
        res+="double u%s=1./(1.+%s);\n"%(sector.subsectors[0].pvar,subs)
        res+="double D=(%s);\n"%(D_)
        res+="double res = %s;\n return res;\n}\n"%expr
        res2+="f+=func%s_%s(%s);\n"%(cnt,index, varstring2)
        cnt+=1
    return res + res2 + "return f;}\n"


def save_sd(name, graph, model):
    name_="%s_%s_"%(name,"O")

    neps=model.target-graph.NLoops()

    lfactor = 1.
    for qi_ in graph._qi.keys():
        lfactor=lfactor/sympy.factorial(graph._qi[qi_]-1)
    if graph._cdet==None:
        A1=poly_exp(graph._det,(-2,0.5), coef=(float(lfactor*graph.sym_coef()), 0))
    else:
        A1=poly_exp(graph._det,(-3,0.5), coef=(float(lfactor*graph.sym_coef()), 0))
    ui=reduce(lambda x, y:x+y,  [[qi_]*(graph._qi[qi_]-1) for qi_ in graph._qi])
    ui=list()
    for qi_ in graph._qi:
        ui+=[qi_]*(graph._qi[qi_]-1)
    A2=poly_exp([ui,], (1, 0))

    ua=list()
    for qi_ in graph._qi:
#    for qi_ in [5,]:
        strechs=list()
        for i in range(len(graph._eqsubgraphs)):
            if qi_ in graph._eqsubgraphs[i]:
                strechs.append(i+1000)
        ua.append(strechs+[qi_,])


    A3=poly_exp(ua,(1,0))
    print
    print "A3 ", A3

    if graph._cdet<>None:
        A4 = poly_exp(graph._cdet,(1,0),coef=(-1,0))


    sub_idx=-1
    for sub in graph._subgraphs:
        sub_idx+=1
        sub._strechvar=1000+sub_idx
        print "%s sub = %s"%(sub._strechvar,  sub)

    strechs = strech_indexes(graph, model)
    print "strechs =", strechs

    Nf = 10000
    maxsize = 50000
    sector_terms = dict()

    idx = -1
    size = 0
    idx_save = 0
    Nsaved = 0
    NZero = 0
    for tree in graph._sectors:
        for subsectors in xTreeElement(tree):
#            print "sector = ", subsectors
            sector = Sector(subsectors)
#            print
#            print "sector = ", sector
            C_= poly_exp([[]],(1,0),coef=(sector.coef,0))
            idx+=1

            if (idx+1) % (Nf/10)==0:
                print "%s " %(idx+1)


            if graph._cdet==None:
                terms=decompose_expr(sector,[A1, A2, A3, C_ ], strechs )
            else:
                terms=decompose_expr(sector,[A1, A2, A3, A4, C_ ], strechs )

#            print "A3=",A3
#            print "A4=",A4
#            print
#            print factorize_poly_lst(terms[0])

            s_terms = list()
            for term in terms:
                s_terms+=diff_subtraction(term, strechs, sector)

            s_terms_=list()
            for term in s_terms:
                if len(term)>0:
                    s_terms_.append(term)
            if len(s_terms_)>0:
                sector_terms[sector] = s_terms_
                size+=s_terms_.__sizeof__()
            else:
                NZero+=1

            if size>=maxsize:
                save_sectors(graph, sector_terms, strechs.keys(), name_, idx_save, neps)
                idx_save+=1
                Nsaved+=len(sector_terms)
                print "saved to file  %s(%s) sectors (%s) size=%s..."%(Nsaved, Nsaved+NZero, idx_save, size)
                sector_terms=dict()
                size=0

    if len(sector_terms)>0:
        save_sectors(graph, sector_terms, strechs.keys(), name_, idx_save, neps)
        idx_save+=1
        Nsaved+=len(sector_terms)
        print "saved to file  %s(%s) sectors (%s) size=%s..."%(Nsaved, Nsaved+NZero, idx_save, size)
        sector_terms=dict()
    for j in range(neps+1):
        f=open("%s_E%s.c"%(name_, j),'w')
        f.write(code(idx_save-1, len(graph._qi.keys())+len(strechs.keys()), "%s_func"%name_, neps=j))
        f.close()


def extract_eps(term):
    leading=list()
    eps_poly=sympy.Number(1)
    e=sympy.var('e')
    log_func=None
    for poly in term:
        if poly.power.b<>0:
            if log_func<>None:
                raise ValueError, "More than one polynom in eps power %s and %s"%(log_func, poly.poly)
            if poly.coef.b <> 0:
                raise ValueError, "Polynom in eps power has nontrivial coef %s"%(poly.coef)
            log_func = copy.deepcopy(poly.poly)
            log_pow = poly.power.b
            poly_=copy.deepcopy(poly)
            poly_.power.b=0
            leading.append(poly_)
        else:
            if poly.coef.b<>0:
                eps_poly=eps_poly*(poly.coef.a+e*poly.coef.b)
                poly_=copy.deepcopy(poly)
                poly_.coef=exp_pow((1,0))
                leading.append(poly_)
            else:
                poly_=copy.deepcopy(poly)
                leading.append(poly_)

    return (leading, eps_poly, log_func, log_pow)


def code( Nf, N,  func_fname, neps=-1):
    include=""
    func="""
void func(double k[DIMENSION], double f[FUNCTIONS])
{
f[0]=0.;
"""

    for i in range(Nf+1):
        func+="""
f[0]+=func_t_%s(k);
"""%i
        if neps<0: #old behavior
            include+="#include \"%s_%s.h\"\n"%(func_fname, i)
        else:
            include+="#include \"%s_%s_E%s.h\"\n"%(func_fname, i,neps)
    func+="}\n\n"


    res="""
#include <math.h>
#include <stdio.h>
#include <vegas.h>
#include <stdlib.h>
#define gamma tgamma
#define DIMENSION %s
#define FUNCTIONS 1
#define ITERATIONS 5
#define NTHREADS 2
#define NEPS 0
#define NITER 2

%s

double reg_initial[2*DIMENSION]={%s};

"""%(N-1, include,  ("0.,"*(N-1)+"1.,"*(N-1))[:-1])
    res+=func + """
int t_gfsr_k;
unsigned int t_gfsr_m[SR_P];
double gfsr_norm;


int main(int argc, char **argv)
{
  int i;
  long long npoints;
  int nthreads;
  int niter;
  double region_delta;
  double reg[2*DIMENSION];
  int idx;
  if(argc >= 2)
    {
      npoints = atoll(argv[1]);

    }
  else
    {
      npoints = ITERATIONS;
    }

  if(argc >= 3)
    {
      nthreads = atoi(argv[2]);

    }
  else
    {
      nthreads = NTHREADS;
    }
   if(argc >= 5)
    {
      region_delta = atof(argv[4]);

    }
  else
    {
      region_delta = 0.;
    }

  if(argc >= 4)
    {
      niter = atoi(argv[3]);

    }
  else
    {
      niter = NITER;
    }

    for(idx=0; idx<2*DIMENSION; idx++)
      {
         if(idx<DIMENSION)
           {
             reg[idx] = reg_initial[idx]+region_delta;
           }
         else
           {
             reg[idx] = reg_initial[idx]-region_delta;
           }
      }
  double estim[FUNCTIONS];   /* estimators for integrals                     */
  double std_dev[FUNCTIONS]; /* standard deviations                          */
  double chi2a[FUNCTIONS];   /* chi^2/n                                      */

  vegas(reg, DIMENSION, func,
        0, npoints/10, 5, NPRN_INPUT | NPRN_RESULT,
        FUNCTIONS, 0, nthreads,
        estim, std_dev, chi2a);
  vegas(reg, DIMENSION, func,
        2, npoints , niter, NPRN_INPUT | NPRN_RESULT,
        FUNCTIONS, 0, nthreads,
        estim, std_dev, chi2a);
double delta= std_dev[0]/estim[0];
printf ("result = %20.18g\\nstd_dev = %20.18g\\ndelta = %20.18g\\n", estim[0], std_dev[0], delta);
//  printf ("Result %d: %g +/- %g delta=%g\\n",NEPS, estim[0], std_dev[0], delta);
//  for (i=1; i<FUNCTIONS; ++i)
//    printf("Result %i:\\t%g +/- %g  \\tdelta=%g\\n", i, estim[i], std_dev[i],std_dev[i]/estim[i]);
  return(0);
}

"""
    return res



def save(name, graph, model, overwrite=True):
    dirname = '%s/%s/%s/'%(model.workdir,method_name, name)
    try:
        os.mkdir('%s/%s'%(model.workdir, method_name))
    except:
        pass
    try:
        os.mkdir(dirname)
    except:
        if overwrite:
            file_list = os.listdir(dirname)
            for file in file_list:
                if fnmatch.fnmatch(file,"*.c") or fnmatch.fnmatch(file,"*.run") or fnmatch.fnmatch(file,"*.o"):
                    os.remove(dirname+file)
    Prepare(graph,model)
    save_sd(dirname+name, graph, model)

def compile(name, model):
    _compile("%s/%s/"%(method_name,name), model, options=["-lm", "-lpthread", "-lpvegas", "-O2"])

def compile_mpi(name, model):
    _compile("%s/%s/"%(method_name,name), model, options=["-lm", "-lpthread_mpi", "-lpvegas", "-O2"], cc="mpicc")


def execute():
    pass

def _compile(name, model, options=list(), cc="gcc"):
    failed=False
    dirname = '%s/%s/'%(model.workdir,name)
    os.chdir(dirname)
    obj_list=dict()
    for file in os.listdir("."):
        if fnmatch.fnmatch(file, "*__func_*.c"):
            regex=re.match('.*_func_\d+_E(\d+)\.c', file)
            if regex:
                eps_num=int(regex.groups()[0])
                if eps_num not in obj_list.keys():
                    obj_list[eps_num]=list()
                obj_list[eps_num].append(file)
            print "Compiling objects %s ..."%file,
            obj_name=file[:-2]+".o"
            try:
                os.remove(obj_name)
            except:
                pass
            process = subprocess.Popen([cc, file] + options + ["-c"] + ["-o", obj_name], shell=False,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            exit_code = process.wait()
            (std_out, std_err) = process.communicate()
            if exit_code <> 0 :
                print "FAILED"
                print std_err
                failed=True
            else:
                if len(std_err) == 0:
                    print "OK"
                else:
                    print "CHECK"
                    print std_err
    print

    for file in os.listdir("."):
        if fnmatch.fnmatch(file, "*.c") and not fnmatch.fnmatch(file,"*__func_*.c"):
            regex=re.match('.*_E(\d+)\.c', file)
            if regex:
                eps_num=int(regex.groups()[0])

            print "Compiling %s ..."%file,
            prog_name=file[:-2]+"_.run"
            try:
                os.remove(prog_name)
            except:
                pass
            process = subprocess.Popen([cc, file] + options + ["-I",".","-L","."] + obj_list[eps_num] + ["-o", prog_name], shell=False,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            exit_code = process.wait()
            (std_out, std_err) = process.communicate()
            if exit_code <> 0 :
                print "FAILED"
                print std_err
                failed=True
            else:
                if len(std_err) == 0:
                    print "OK"
                else:
                    print "CHECK"
                    print std_err

    return not failed