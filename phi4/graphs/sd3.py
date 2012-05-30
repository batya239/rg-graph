#!/usr/bin/python
# -*- coding: utf8
import copy
from comb import xUniqueCombinations
import conserv
from methods.feynman_tools import conv_sub
from methods.feynman_tools import find_eq, apply_eq, qi_lambda, merge_grp_qi, dTau_line

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
        print secondary_vars, self.svars
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
        print cons1
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
    print qi2l
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

    print  pvars

    for i in range(len(sector)):
        for j in range(len(subgraphs)):
            if pvars[i] in subgraphs[j]:
                subgraphs_cnt_total[j] += 1

    for i in range(start, len(sector)):
        for j in range(len(subgraphs)):
            if pvars[i] in subgraphs[j]:
                subgraphs_cnt[j] += 1
        print "sector:", sector,"i=", i
        print pvars[:i + 1], subgraphs_cnt, subgraphs_cnt_total, CheckForDs(subgraphs_cnt, subgraphs_cnt_total, subgraph_loops, subgraph_dims, sector.ds)

        cfds = CheckForDs(subgraphs_cnt, subgraphs_cnt_total, subgraph_loops, subgraph_dims, sector.ds)
        if cfds <> None:
            _asector = sector.cut(i + 1)
            _asector.SetDS(i, cfds, 0)
            _asector.SplitDomain(graph,cfds)
            print _asector, _asector.domains
            print "speer ", _SpeerSectors([_asector])
            for __sector in _SpeerSectors([_asector]):

                asectors+=ASectors(__sector,graph, model, start=len(_asector.PrimaryVars()))
            sector.SetDS(i, cfds, 1)

    print "sector = ", sector
    print "asectors = ", asectors
    return [sector] + asectors


def gensectors(graph, model):
    speer = SpeerSectors(graph, model)

    res = list()
    for sector in speer:
        res+=ASectors(sector, graph, model)

    return res


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

    g1 = dTau_line(graph, 5, model)
    FeynmanSubgraphs(g1, model)
    g1._eqsubgraphs = apply_eq_onsub(graph._qi2l, conv_sub(g1._subgraphs))

    graph._sectors = gensectors(g1, model)
    #    graph._det=gendet(cons, graph._subgraphs, graph._qi, graph.NLoops())