#!/usr/bin/python
# -*- coding:utf8

import sympy

from roperation import feynman_qi_lambda, feynman_B, decompose_B, SubsSquaresStrechs

def Prepare(graph):
    (graph._qi, graph._qi2line)=feynman_qi_lambda(graph)
    B=feynman_B(graph._qi)
    (c,b,v)=decompose_B(B)
    det=v.det()
    Cdet=((b.transpose()*v.adjugate()*b)[0] -c*det).expand()

    graph._det_f=SubsSquaresStrechs(det)
    graph._cdet=SubsSquaresStrechs(Cdet)
    

def dTau_line(graph, qi,  model):
#FIXME: choose most suitable line for qi?
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
            res[sub._sterch_var]=-1
        elif dim==0:
            res[sub._sterch_var]=1
        elif dim==2:
            res[sub._strech_var]=2
        else:
            raise ValueError, "Unsupported subgaphs dim = %s"%dim
    return res
            

        
def feynman_term(graph, qi, model):
    g_qi=dTau_line(graph, qi,  model)
    strechs=strech_indexes(g_qi, model)
    det=g_qi._det_f
    cdet=g_qi._cdet
    e=sympy.var('e')
    res=1./det**(2.-e/2.)
    
    for i in range(len(graph._qi.keys())):
        q=graph._qi.keys()[i]
        ui=sympy.var('u_%s'%i)
        if graph._qi[q]>1:
            res=res*ui**(graph._qi[q]-1)
        if q==qi:
            res=res*ui
        res=res/sympy.factorial(graph._qi[q]-1)
    if len(graph.ExternalLines())==2:
        res=res*cdet/det
        
    for ai in strechs:
        ai_=sympy.var(ai)
        if strechs[ai]==-1:
            res=res.sub(ai_, 1.)
        elif strechs[ai]==1:
            res=res.diff(ai_)
        elif strechs[ai]==2:
            res=res.diff(ai_).diff(ai_)*(1-ai_)
            
#TODO: add gammas Gamma(1+ne/2)*Gamma(2-e/2)**n ??.
    return res
            
    
        
