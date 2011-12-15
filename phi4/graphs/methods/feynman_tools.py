#!/usr/bin/python
# -*- coding:utf8

import sympy

#from .. import conserv
#from .. import comb
import conserv
import comb

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

def det_as_lst(cons):
    eqs = find_eq(cons)
    cons=apply_eq(cons, eqs)
    ui=list(unique_ui(cons))
    det_start = [x for x in comb.xUniqueCombinations(ui, graph.NLoops())]
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

def det(cons, subgraphs_):
    det_lst=det_as_lst(graph)
    res=0
    for term in det_lst:
        sterm=1
        for term2 in term:
            ui=sympy.var('u_%s'%term2)
            strem*=ui
        
