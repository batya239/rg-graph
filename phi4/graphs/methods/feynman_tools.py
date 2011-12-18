#!/usr/bin/python
# -*- coding:utf8

import sympy

#from .. import conserv
#from .. import comb
import conserv
import comb
import subgraphs

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
    
def qi_lambda(cons):
    eqs=find_eq(cons)
    qi=dict()
    qi2line=dict()
    for ui in unique_ui(cons):
        qi[ui]=1
        qi2line[ui]=[ui]
    for eq in eqs:
        ui=eqs[eq]
        qi[ui]+=1
        qi2line[ui].append(eq)
    return (qi, qi2line)

def det_as_lst(cons, nloops):
    eqs = find_eq(cons)
    cons=apply_eq(cons, eqs)
    ui=list(unique_ui(cons))
    det_start = [x for x in comb.xUniqueCombinations(ui, nloops)]
# реализовать равенство ui
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
        res+=sterm
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
    graph._qi, qi2l = qi_lambda(cons)
    
    det_ = det(cons, graph._subgraphs,  graph.NLoops())
    Cdet=0
    if len(graph.ExternalLines())==2:
        int_edges[1000000]=[i.idx() for i in graph.ExternalNodes()]
        cons = conserv.Conservations(int_edges)
        Cdet = det(cons, graph._subgraphs,  graph.NLoops()+1)
    
    graph._det_f=det_
    graph._cdet=Cdet
