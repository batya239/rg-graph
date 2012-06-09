#!/usr/bin/python
# -*- coding: utf8
import copy
import sympy
from comb import xUniqueCombinations
import conserv
from methods.feynman_tools import conv_sub, strech_indexes
from methods.feynman_tools import find_eq, apply_eq, qi_lambda, merge_grp_qi, dTau_line
from sd2 import poly_exp, factorize_poly_lst, set1_poly_lst, set0_poly_lst, minus, diff_poly_lst

import subgraphs

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

#    FindExtendedTadpoles(graph)

class Sector:
    def __init__(self, sect_list, coef=1):
        """
        sector (sec_list -> list of SubSectors),
        coef - coefficient of this sector (symmetries)
        """
        self.subsectors = copy.deepcopy(sect_list)
        self.ds = {}
        self.coef = coef
        self._UpdateDS()
        self.domains = []
        self.excluded_vars = list()

    def __len__(self):
        return len(self.subsectors)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.subsectors)

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


class SubSector:
    def __init__(self, primary_var, secondary_vars, primary=False, ds_vars=None):
        self.pvar = primary_var

        self.svars = sorted(secondary_vars)
#        print secondary_vars, self.svars
        self.primary = primary
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


class Domain:
    def __init__(self, vars, conservations, model):
        self.vars = vars
        self.cons = conservations
        self.model = model

    def __repr__(self):
        return str(self.vars)

    def split(self, graph, subgraph_idx):
        """
        split domain
        """
#        subgraph_lines = [x.idx() for x in subgraph._lines]
        subgraph_lines = graph._eqsubgraphs[subgraph_idx]
        subgraph = graph._subgraphs[subgraph_idx]
        if not set(subgraph_lines).issubset(set(self.vars)):
            raise ValueError, "Cant split domain %s using subgraph %s"%(self.vars, subgraph_lines)
        vars1=list(set(subgraph_lines) & set(self.vars))
        vars2=list(set(self.vars) - set(subgraph_lines))
        cons1=set([])
        cons2=copy.copy(self.cons)
        for cons_ in self.cons:
            cons__=frozenset(set(cons_)&set(vars1))
            if len(cons__)>0:
                cons1 = cons1 | set([cons__])
#        print cons1
        for cons_ in xUniqueCombinations(vars1, subgraph.Dim(self.model)):
            cons2 = cons2 | set([frozenset(cons_)])
        return (Domain(vars1, cons1, self.model), Domain(vars2, cons2, self.model))



def decompose(var_list, primary=False):
    """
    generates list of subsectors for decomposition by vars in var_list
    """
    subsectors = []
    for var in var_list:
        _vars = copy.copy(var_list)
        _vars.remove(var)
        subsectors.append(SubSector(var, _vars, primary=primary))
    return subsectors

def SetPrimaryDomain(sector, vars,cons, model):
    sector.domains=[Domain(vars, cons, model)]

def PrimarySectors(vars):
    """
    Generates primary sectors for decomposition
    """
    return map(Sector, [[x] for x in decompose(vars, primary=True)])


def check_cons(term, cons):
    """
    check if the combination of vars denied by conservation laws
    """
    res = True
    for constr in cons:
        if constr.issubset(term):
            res = False
            break
    return res

def _SpeerSectors(start_sectors):
    stop = False
    sectors = start_sectors

    final = []
    while not stop:
        stop = True
        _sectors = []
        for sector in sectors:
#            print "SS sector",sector, sector.domains
            pvars = sector.PrimaryVars()
            _domain=False
            for domain in sector.domains:
#                print "SS domain",domain
                vars_ = list(set(domain.vars)-set(pvars))
                vars = list()
                for var in vars_:
                    if check_cons(pvars+[var], domain.cons):
                        vars.append(var)
                if len(vars)>1:
#                    print "SS vars",vars
                    for subsector in decompose(vars):
                        _domain = True
                        _sectors.append(sector + subsector)
                    break
#                print "SS _domein",_domain
            if _domain:
                stop = False
            else:
                final.append(sector)
#            print "SS -----"
#            print "SS final", final
#            print "SS _sectors",_sectors
        sectors=_sectors
    final += sectors
    return final




def SpeerSectors(graph, model):
    """
    Generates Speer? sectors
    """
    sectors = PrimarySectors(graph._qi.keys())
    for sector in sectors:
        SetPrimaryDomain(sector, graph._qi.keys(), graph._cons, model)
    sectors=_SpeerSectors(sectors)
#    print sectors
    return sectors




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


def CheckForDs(subgraphs_cnt, subgraphs_total, subgraph_loops, subgraph_dims, ds):
    """
    check if direct subtraction is possible for current decomposition
    """
    for i in subgraphs_cnt.keys():
#        print
#        print i
#        print subgraphs_total, subgraph_loops

        if subgraphs_total[i] >= subgraph_loops[i] + 1:
#         if True:
            if subgraphs_cnt[i] >= RequiredDecompositions(subgraph_dims[i]) and i not in ds.keys():
                return i
    return None

def apply_eq_onsub(qi2l, subgraphs_as_set):
#    print qi2l
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



def ASectors(sector, graph, model, start=0):
    """
    generate sectors for strech parameters eq 0
    """
    subgraphs = conv_sub(graph._subgraphs)
    subgraph_dims = []
    subgraph_loops = []
    for x in graph._subgraphs:
        subgraph_dims.append(x.Dim(model))
        subgraph_loops.append(x.NLoopSub())
    #    print subgraphs
    #    print subgraph_dims

    subgraphs_cnt = dict([(i, 0) for i in range(len(subgraphs))])
    subgraphs_cnt_total = dict([(i, 0) for i in range(len(subgraphs))])
    pvars = sector.PrimaryVars()


    asectors = list()

#    print  pvars

    for i in range(len(sector)):
        for j in range(len(subgraphs)):
            if pvars[i] in subgraphs[j]:
                subgraphs_cnt_total[j] += 1

    for i in range(start, len(sector)):
        for j in range(len(subgraphs)):
            if pvars[i] in subgraphs[j]:
                subgraphs_cnt[j] += 1
#        print "sector:", sector,"i=", i
#        print pvars[:i + 1], subgraphs_cnt, subgraphs_cnt_total, CheckForDs(subgraphs_cnt, subgraphs_cnt_total, subgraph_loops, subgraph_dims, sector.ds)

        cfds = CheckForDs(subgraphs_cnt, subgraphs_cnt_total, subgraph_loops, subgraph_dims, sector.ds)
        if cfds <> None:
            _asector = sector.cut(i + 1)
            _asector.SetDS(i, cfds, 0)
            _asector.SplitDomain(graph,cfds)
#            print _asector, _asector.domains
#            print "speer ", _SpeerSectors([_asector])
            for __sector in _SpeerSectors([_asector]):

                asectors+=ASectors(__sector,graph, model, start=len(_asector.PrimaryVars()))
            sector.SetDS(i, cfds, 1)

#    print "sector = ", sector
#    print "asectors = ", asectors
    return [sector] + asectors


def gensectors(graph, model):
    speer = SpeerSectors(graph, model)

    res = list()
    for sector in speer:
        res+=ASectors(sector, graph, model)

    return list(set(res))

def strech_list(sector, subgraphs_):
    """ generate list of strechs extracted in leading term by first pass of sector decomposition
    """

    strechs=[]
    subs=conv_sub(subgraphs_)
    for j in range(len(subs)):
        si=len(set(sector)&set(subs[j]))-subgraphs_[j].NLoopSub()
        strechs+=[1000+j]*si
    return list(set(strechs))

def gendet(cons, subgraphs_, vars, L):
    det=[]
    subs=conv_sub(subgraphs_)
    for i in xUniqueCombinations(vars.keys(),L):
        if check_cons(i, cons):
            det.append(i+strech_list(i, subgraphs_))
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

#    g1 = dTau_line(graph, 5, model)
    FeynmanSubgraphs(graph, model)
    graph._eqsubgraphs = apply_eq_onsub(graph._qi2l, conv_sub(graph._subgraphs))

    graph._det=gendet(cons, graph._subgraphs, graph._qi, graph.NLoops())
    graph._sectors = gensectors(graph, model)
    #    graph._det=gendet(cons, graph._subgraphs, graph._qi, graph.NLoops())

def jakob_poly(sector):
    res = list()
    for subsector in sector.subsectors:
        res+=[subsector.pvar]*len(subsector.svars)
        if subsector.primary:
            res+=[subsector.pvar]
    return res

def decompose_expr(sector,poly_lst, strechs, jakob=True):
    jakobian=jakob_poly(sector)
    res = copy.copy(poly_lst)
    for subsector in sector.subsectors:
        res_n = list()
        for poly in res:
#            print poly
#            print subsector.pvar,subsector.svars
            res_n.append(poly.strech(subsector.pvar,subsector.svars))
#            print poly.strech(subsector.pvar,subsector.svars)
#            print
        res = res_n
    if jakob:
        res.append(poly_exp([jakobian],(1,0), coef=(1,0)))
    # factorization omitted for eps-series implementation
    #res = factorize_poly_lst(res)

#    print strechs
#    print sector, sector.ds
#    print res
    terms=[res]
    for strech in strechs:
        sidx=strech
        terms_n=[]
        if strechs[strech]==0:
#            print (sidx in sector.ds.keys() , sector.ds[sidx]!=1)
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
#    print terms

    return terms



def save_sd(name, g1,  model):

    if len(g1._subgraphs)==0:
        no_dm2=True
        g1._eq_grp=[None]
    else:
        no_dm2=False

    for grp_ in g1._eq_grp:
        if (not no_dm2) and len(grp_) == 0:
            continue
        print grp_  ,  g1._qi,
        if not no_dm2:
            print list(set(grp_)& set(g1._qi))
        else:
            print

        ui=reduce(lambda x, y:x+y,  [[qi_]*(g1._qi[qi_]-1) for qi_ in g1._qi])

        if not no_dm2:
            qi=list(set(grp_)&set(g1._qi))[0]
            ui.append(qi)
        else:
            qi="O"
        name_="%s_%s_"%(name, qi)

        print "   term u%s"%qi
        print ui,  g1._eq_grp
        sub_idx=-1
        for sub in g1._subgraphs:
            sub_idx+=1
            sub._strechvar=1000+sub_idx
            print "%s sub = %s"%(sub._strechvar,  sub)

        lfactor=1.

        for qi_ in g1._qi.keys():
            if (not no_dm2) and qi_==qi:
                lfactor=lfactor/sympy.factorial(g1._qi[qi_])
            else:
                lfactor=lfactor/sympy.factorial(g1._qi[qi_]-1)


        if not no_dm2:
            grp=None
            for grp in g1._eq_grp:
                if qi in grp:
                    break
            grp_factor=len(grp)
        else:
            grp_factor=1.

        print lfactor, g1.sym_coef(), grp_factor

        A1=poly_exp(g1._det, (-2, 0),  coef=(float(lfactor*g1.sym_coef()*grp_factor ), 0))

#        zeroes=minimal_zeroes(find_zeroes(A1) )
#        print "Zeroes %s:\n%s\n"%(len(zeroes), zeroes)
        print "DET=", A1

        A2=poly_exp([ui, ], (1, 0))
#        strechs=strech_indexes(g1, model)
#        print "strechs = ", strechs
        if not no_dm2:
            g_qi=dTau_line(g1, qi,  model)
        else:
            g_qi=g1

        strechs=strech_indexes(g_qi, model)
        print "strechs = ", strechs
        #print [A1, A2, A3 ]

        strech_vars=[]
        for var in strechs:
            if strechs[var]>0:
                strech_vars.append(var)

        Nf=300
        #        Nf=10


        #        g1._sectors=[[9, 8, 5]]

        #        g1._sectors=[[8, 11, 12, 7, 6]]
        #        g1._sectors=[[12, 13, 7, 10, 11]]
        #        g1._sectors=[[7, 8, 10, 11, 12]]
        #        g1._sectors=[[12, 13, 10, 9, 8]]
        #        g1._sectors=[[13, 11, 12, 10, 7]]
#        drop_azero_terms=False
#        second_decompose=True  # for debugging
        #        second_decompose=False
        #        (second_decompose, drop_azero_terms)=(False,  True)

        sector_terms=dict()

        idx=-1
        idx_save=0
        Nsaved=0
        for sector in g1._sectors:
            current_terms=dict()
            idx+=1

            if (idx+1) % (Nf/10)==0:
                print "%s " %(idx+1)


#            d_strechs=dict([(x, strechs[x]) for x in strech_list(sector.PrimaryVars(), g1._subgraphs)])
#            print d_strechs
            terms=decompose_expr(sector,[A1, A2 ], strechs )
            print "sector: ", sector
            print "decomposed: ", terms
            print
            sector_terms[sector] = terms

            if len(sector_terms)>=Nf:
                save_sectors(g1,sector_terms,strech_vars,name_,idx_save)
                idx_save+=1
                Nsaved+=len(sector_terms)
                print "saved to file  %s sectors (%s) ..."%(Nsaved,idx_save)
                sector_terms=dict()

        if len(sector_terms)>0:
            save_sectors(g1,sector_terms,strech_vars,name_,idx_save)
            idx_save+=1
            Nsaved+=len(sector_terms)
            print "saved to file  %s sectors (%s) ..."%(Nsaved,idx_save)
            sector_terms=dict()
        f=open("tmp/%s.c"%(name_),'w')
        f.write(code(idx_save-1, len(g1._qi.keys())+len(strech_vars), "%s_func"%name_))
        f.close()


