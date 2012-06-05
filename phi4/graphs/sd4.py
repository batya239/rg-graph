#!/usr/bin/python
# -*- coding: utf8
import copy
import sympy
from comb import xUniqueCombinations
import conserv
from methods.feynman_tools import merge_grp_qi, conv_sub, qi_lambda, apply_eq, find_eq, strech_indexes
from sd2 import poly_exp, code, factorize_poly_lst, poly_list2ccode, code_f, code_h, diff_subtraction, set1_poly_lst, diff_poly_lst
from sd3 import FeynmanSubgraphs, apply_eq_onsub, check_cons, Domain, RequiredDecompositions, SubSector, decompose_expr, Sector

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

def xTreeElement(sector_tree, parents=list()):

    if len(sector_tree.branches) == 0:
        parents_=parents + [SubSector(sector_tree.pvar,sector_tree.svars,primary=sector_tree.primary, ds_vars=sector_tree.ds)]
        yield parents_
    else:
        for branch in sector_tree.branches:
        #            print sector_tree.pvar, sector_tree.svars, [x.str() for x in sector_tree.branches]
            parents_=parents + [SubSector(sector_tree.pvar,sector_tree.svars,primary=sector_tree.primary)]
            for term in xTreeElement(branch, parents_):
                yield term



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
    t_=list()
    for tree in speer_trees:
        t_+=[x for x in xTreeElement(tree)]
    print "speer_sectors:",len(t_)
    ASectors(speer_trees,graph)
    return speer_trees

def gendet(graph, N=None):
    if N==None:
        N_=graph.NLoops()
    else:
        N_=N
    det=[]
    subs=graph._eqsubgraphs
    for i in xUniqueCombinations(graph._qi2l.keys(), N_):
        if check_cons(i, graph._cons):
            det.append(i+strech_list(i, graph))
    return det


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
        Cdet = gendet(graph_, N=graph.NLoops()+1) #TODO minus
        print len(Cdet)
        print "Cdet= ",Cdet
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

    #graph._eqsubgraphs = apply_eq_onsub(graph._qi2l, conv_sub(graph._subgraphs))



    graph._subgraph_dims=[x.Dim(model) for x in graph._subgraphs]

    graph._det = gendet(graph)
    print len(graph._det)
    print "det=",graph._det
    graph._sectors = gensectors(graph, model)
    t_=0
    for tree in graph._sectors:
        t_+=len([x for x in xTreeElement(tree)])
    print "A_sectors: ",t_

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



        expr, subs=poly_dict[sector]
        res+="double u%s=1./(1.+%s);\n"%(sector.subsectors[0].pvar,subs)
        res+="double res = %s;\n return res;\n}\n"%expr
        res2+="f+=func%s_%s(%s);\n"%(cnt,index, varstring2)
        cnt+=1
    return res + res2 + "return f;}\n"


def save_sectors(g1, sector_terms, strech_vars, name_, idx):

    sect_terms=dict()
    for sector in sector_terms.keys():

    #            print "sector= ",  sector
    #            print "qi = ", g1._qi
        subs=[[x] for x in g1._qi.keys()]
        subs.remove([sector.subsectors[0].pvar])

        subs_polyl=decompose_expr(Sector(sector.subsectors[1:]), [poly_exp(subs,  (1, 0))], list() , jakob=False)
        if len(subs_polyl)<>1:
            raise Exception, "invalid decomposition for delta function term"

        terms=sector_terms[sector]
        tres=""
        for term in   terms:
            f_term=factorize_poly_lst(term)
            tres+="%s;\nres+="%poly_list2ccode(f_term)
        sect_terms[sector]=(tres[:-5], poly_list2ccode(subs_polyl[0]))


    #        print
    #        print "write to disk... %s"%(idx+1)
    f=open("tmp/%s_func_%s.c"%(name_,idx),'w')
    f.write(code_f(functions(sect_terms, g1._qi.keys(), strech_vars, idx), len(g1._qi.keys())+len(strech_vars)))
    f.close()
    f=open("tmp/%s_func_%s.h"%(name_,idx),'w')
    f.write(code_h( idx, len(g1._qi.keys())+len(strech_vars)))
    f.close()

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


def save_sd(name, graph, model):
    name_="%s_%s_"%(name,"O")
    lfactor = 1.
    for qi_ in graph._qi.keys():
        lfactor=lfactor/sympy.factorial(graph._qi[qi_]-1)
    if graph._cdet==None:
        A1=poly_exp(graph._det,(-2,0), coef=(float(lfactor*graph.sym_coef()), 0))
    else:
        A1=poly_exp(graph._det,(-3,0), coef=(float(lfactor*graph.sym_coef()), 0))
    ui=reduce(lambda x, y:x+y,  [[qi_]*(graph._qi[qi_]-1) for qi_ in graph._qi])
    ui=list()
    for qi_ in graph._qi:
        ui+=[qi_]*(graph._qi[qi_]-1)
    A2=poly_exp([ui,], (1, 0))

    ua=list()
    for qi_ in graph._qi:
        strechs=list()
        for i in range(len(graph._eqsubgraphs)):
            if qi_ in graph._eqsubgraphs[i]:
                strechs.append(i+1000)
        ua.append(strechs+[qi_,])


    A3=poly_exp(ua,(1,0))

#    print "A3 = ", A3

    if graph._cdet<>None:
        A4 = poly_exp(graph._cdet,(1,0),coef=(-1,0))


    sub_idx=-1
    for sub in graph._subgraphs:
        sub_idx+=1
        sub._strechvar=1000+sub_idx
        print "%s sub = %s"%(sub._strechvar,  sub)

    strechs = strech_indexes(graph, model)
    print "strechs =", strechs

    Nf=10000
    maxsize=50000
    sector_terms=dict()

    idx=-1
    size=0
    idx_save=0
    Nsaved=0
    for tree in graph._sectors:
        for subsectors in xTreeElement(tree):
#            print "sector = ", subsectors
            sector=Sector(subsectors)

            current_terms=dict()
            idx+=1

            if (idx+1) % (Nf/10)==0:
                print "%s " %(idx+1)


        #            d_strechs=dict([(x, strechs[x]) for x in strech_list(sector.PrimaryVars(), g1._subgraphs)])
        #            print d_strechs
            if graph._cdet==None:
                terms=decompose_expr(sector,[A1, A2, A3 ], strechs )
            else:
#                print A4
                terms=decompose_expr(sector,[A1, A2, A3, A4 ], strechs )
#            print "decomposed: ", terms
#            print
            s_terms = list()
            for term in terms:
                #print term
                s_terms+=diff_subtraction(term, strechs, sector)
            #print s_terms

#            print


            sector_terms[sector] = s_terms

            size+=s_terms.__sizeof__()

            if size>=maxsize:
                save_sectors(graph, sector_terms, strechs.keys(), name_, idx_save)
                idx_save+=1
                Nsaved+=len(sector_terms)
                print "saved to file  %s sectors (%s) size=%s..."%(Nsaved, idx_save, size)
                sector_terms=dict()
                size=0

    if len(sector_terms)>0:
        save_sectors(graph, sector_terms, strechs.keys(), name_, idx_save)
        idx_save+=1
        Nsaved+=len(sector_terms)
        print "saved to file  %s sectors (%s) size=%s..."%(Nsaved,idx_save,size)
        sector_terms=dict()
    f=open("tmp/%s.c"%(name_),'w')
    f.write(code(idx_save-1, len(graph._qi.keys())+len(strechs.keys()), "%s_func"%name_))
    f.close()




