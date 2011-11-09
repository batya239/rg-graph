#!/usr/bin/python
# -*- coding:utf8

import sympy
from sympy import Symbol
import os
import re as regex
import fnmatch
import utils
import time


from roperation import feynman_qi_lambda, feynman_B, decompose_B, SubsSquaresStrechs
import calculate
import utils

from feynman import *

        
def feynman_term(graph, qi, model):
    g_qi=dTau_line(graph, qi,  model)
    strechs=strech_indexes(g_qi, model)
    strechs_orig=strech_indexes(graph, model)
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
        if strechs_orig[ai] - strechs[ai]==1 :
            res=res*ai_
        elif strechs_orig[ai] - strechs[ai]<>0:
            raise ValueError,  " strech %s problem: %s %s"%(ai, strechs_orig[ai], strechs[ai])
        
            
        if strechs_orig[ai]==1:
            res=res.diff(ai_)
        elif strechs_orig[ai]==2:
            res=res.diff(ai_).diff(ai_)*(1-ai_)
        else:
            raise ValueError,  " invalid strech count %s -> %s"%(ai, strech_orig[ai])
            
#TODO: add gammas Gamma(1+ne/2)*Gamma(2-e/2)**n ??.
    return res

        
def save(name, graph, model, overwrite=True):
    dirname = '%s/%s/feynmanA/'%(model.workdir,name)
    try:
        os.mkdir('%s/%s/'%(model.workdir,name))
    except:
        pass
    try:
        os.mkdir(dirname)
    except:
        if overwrite:
            file_list = os.listdir(dirname)
            for file in file_list:
                if fnmatch.fnmatch(file,"*.c") or fnmatch.fnmatch(file,"*.run"):
                    os.remove(dirname+file)
                    
    Prepare(graph)
    print "det(v)=", graph._det_f
    print "det(v)*C = ", graph._cdet    
    e=sympy.var('e')
    cnt=0
    expr=0
    for qi in graph._qi:
        expr+=feynman_term(graph, qi, model)
    eps_cnt=0
    for _expr in utils.series_lst(expr, e,  model.target - graph.NLoops()):
        integrand=subs_vars(_expr)
        integrand+= "\nf[0]=1.0e-38;\n"
        integrand+= "f[0]+=factor*(%s);\n"%( sympy.printing.ccode(_expr*graph.sym_coef()))
        f=open('%s/%s_E%s_O.c'%(dirname,name,eps_cnt),'w')
        f.write(calculate.core_pv_code(integrand))
        f.close()
        eps_cnt+=1
         
                    

def compile(name,model):
    calculate.compile("%s/feynmanA"%name, model)

def execute(name, model, points=10000, threads=4, calc_delta=0., neps=0):
    return calculate.execute("%s/feynmanA"%name, model, points=points, threads=threads, calc_delta=calc_delta, neps=neps)
    

