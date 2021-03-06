#!/usr/bin/python
# -*- coding:utf8

import re

import sympy

#from .. import conserv
#from .. import comb
import conserv
import comb
import subgraphs
import utils

def merge_grp_qi(eq_grp, qi2l):
    d=dict()
    for set_ in eq_grp+qi2l.values():
       for var in set_:
           if var not in d:
               d[var]=set_
           else:
               d[var]=tuple(set(d[var])|set(set_))
    return list(set(d.values()))


def line_to_qi(graph, line_idx):
    for qi in graph._qi2l.keys():
        if line_idx in graph._qi2l[qi]:
            return qi
    

def find_eq(cons):
    res=dict()
    for tcons in cons:
        if len(tcons)==2:
            a, b=tuple(tcons)
            if not b in res.keys():
                res[a]=b
            else:
                res[a]=res[b]
    return res
    
def apply_eq(cons, eqs):
    res=set()
    for tcons in cons:
        tcons2 = set(tcons)
        for eq in eqs:
            if eq in tcons2:
                if set([eq, eqs[eq]]).issubset(tcons2):
                    tcons2=tcons2- set([eq, eqs[eq]])
                else:
                    tcons2=(tcons2-set([eq])) | set([eqs[eq]])
        tcons2=frozenset(tcons2)
        if len(tcons2)>1:
            res=res|set([tcons2])
    return res
    
def unique_ui(cons):
    res=set()
    for tcons in cons:
        res=res|tcons
    res=res-set([1000000])
    return res
    
def qi_lambda(cons, eqs):
    qi=dict()
    qi2line=dict()
#    print cons, eqs
    for ui in unique_ui(cons):
        qi[ui]=1
        qi2line[ui]=[ui]
    for eq in eqs:
        ui=eqs[eq]
        if len(cons)==0:
            qi[ui]=0
            qi2line[ui]=[ui]
        qi[ui]+=1
        qi2line[ui].append(eq)
    return (qi, qi2line)

def det_as_lst(cons, nloops):
    ui=list(unique_ui(cons))
    det_start = [x for x in comb.xUniqueCombinations(ui, nloops)]
    det=list()
    for term in det_start:
        valid = True
        for cterm in cons:
            if cterm.issubset(term):
                valid = False
                break
        if valid:
            det.append(term)
    return det
    
def _adet_as_lst(cons, nloops):
    """ helper function for testing purposes
    """
    det=det_as_lst(cons, nloops)
    ui=unique_ui(cons)
    res=list()
    for term in det:
        t2=list(ui-set(term))
        t2.sort()
        res.append(t2)
    return res
        
    
def conv_sub(subgraphs_):
    res=list()
    for sub in subgraphs_:
        tsub=[i.idx() for i in sub._lines]
        res.append(tsub)
    return res

def strechname(sub_i):
    name="a"
    for t in sub_i:
        name+="_%s"%t
    return name

def det(cons, subgraphs_, nloops):
    det_lst=det_as_lst(cons, nloops)
    if len(cons)==0:
        return sympy.Number(1.)
    res=0
    subs=conv_sub(subgraphs_)
    for term in det_lst:
        sterm=1
        for term2 in term:
            ui=sympy.var('u_%s'%term2)
            sterm*=ui
        for i in range(len(subs)):
            si=len(set(term)&set(subs[i]))-subgraphs_[i].NLoopSub()
            if si>0:
                ai=sympy.var('a_%s'%subgraphs_[i].asLinesIdxStr())
                sterm*=ai**si
                subgraphs_[i]._strechvar=str(ai)
#?                subgraphs_[i]._diffcnt=
        res+=sterm
    return res


def remove_strechs(expr):
    res=expr
    for atom in expr.atoms(sympy.Symbol):
        regex=re.match('^a_', str(atom))
        if regex:
            res=res.subs(atom, 1)
    return res

def Prepare(graph, model):
    model.SetTypes(graph)
    model.checktadpoles=False
    graph.FindSubgraphs(model)
    
    subs_toremove=subgraphs.DetectSauseges(graph._subgraphs)
    graph.RemoveSubgaphs(subs_toremove)

    subgraphs.RemoveTadpoles(graph)
    
    int_edges=graph._internal_edges_dict()
    cons = conserv.Conservations(int_edges)
    eqs = find_eq(cons)
#    print cons, eqs
    cons=apply_eq(cons, eqs)
    graph._cons=cons
    graph._qi, graph._qi2l = qi_lambda(cons, eqs)
    
    graph._eq_grp_orig=graph._eq_grp
    graph._eq_grp=merge_grp_qi(graph._eq_grp, graph._qi2l)

    det_ = det(cons, graph._subgraphs,  graph.NLoops())
    Cdet=sympy.Number(0)
    if len(graph.ExternalLines())==2:
        int_edges[1000000]=[i.idx() for i in graph.ExternalNodes()]
        cons = conserv.Conservations(int_edges)
        eqs = find_eq(cons)
        cons=apply_eq(cons, eqs)        
        Cdet = - det(cons, graph._subgraphs,  graph.NLoops()+1)
    
    graph._det_f=det_
    graph._cdet=Cdet
    
def normalize(graph, result):
    (res_, err_)=result
    n=graph.NLoops()
    e=sympy.var('e')
    res=0.
    err=0.
    
    for i in range(len(res_)):
        res+=e**i*res_[i]
        err+=e**i*abs(err_[i])
    res=res*sympy.special.gamma_functions.gamma(1+n*e/2.)*sympy.special.gamma_functions.gamma(2-e/2.)**n/2**n
    err=err*sympy.special.gamma_functions.gamma(1+n*e/2.)*sympy.special.gamma_functions.gamma(2-e/2.)**n/2**n
    
    return ([float(i) for i in utils.series_lst(res, e,  len(res_)-1)], [float(i) for i in utils.series_lst(err, e,  len(res_)-1)])
def dTau_line(graph, qi,  model):
#FIXME: choose most suitable line for qi?
    if isinstance(qi, int):
        line=graph._lines[qi] #hack for feynman_tools
    else:
        line=graph._qi2line[qi][0]

    if model.checkmodifier(line,'tau'):
        idx=graph.Lines().index(line)
        g=graph.Clone()
        newline=g._Line(idx)
        newline.AddModifier("tau")
        return g
    else:
        raise Exception,  "something wrong! :)"
        
def strech_indexes(g_qi, model):
    res=dict()
    for sub in g_qi._subgraphs:
        dim=sub.Dim(model)
        if dim<0:
            res[sub._strechvar]=0
        elif dim==0:
            res[sub._strechvar]=1
        elif dim==2:
            res[sub._strechvar]=2
        else:
            raise ValueError, "Unsupported subgaphs dim = %s"%dim
    return res
            
