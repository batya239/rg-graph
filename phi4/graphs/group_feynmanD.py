#!/usr/bin/python
# -*- coding:utf8

import sympy
from sympy import Symbol
import os
import re as regex
import fnmatch
import utils
import time

from sympy.printing.ccode import ccode

from utils import diff

from roperation import feynman_qi_lambda, feynman_B, decompose_B, SubsSquaresStrechs


import calculate
import utils
import re as regex

from feynman import *


from feynmanD import nintegrations, term_func,  diff_by_strechs,  symplify_expr
    
def feynman_D_func(graph, model):
    
    det=graph._det_f
    cdet=graph._cdet
    name=str(graph.GenerateNickel()).replace('-', '_')
    
    func=dict()
    lfactor=1.
    for qi in graph._qi.keys():
        lfactor=lfactor/sympy.factorial(graph._qi[qi]-1)
    
    for i in range(len(graph._qi.keys())):
        print "   term %s %s"%(name, i)
        qi = graph._qi.keys()[i]
        g_qi=dTau_line(graph, qi,  model)
        strechs=strech_indexes(g_qi, model)
        
        U=sympy.Number(1.)*lfactor
        
        for j in range(len(graph._qi.keys())):
            q=graph._qi.keys()[j]
            ui=sympy.var('u_%s'%j)
            if graph._qi[q]>1:
                U=U*ui**(graph._qi[q]-1)
            if q==qi:
                U=U*ui
        
        A=sympy.Number(1.)
        det_=det
        cdet_=cdet
        for ai in strechs:
            ai_=sympy.var(ai)
            if strechs[ai]==0:
                det_=det_.subs(ai_, 1)
                cdet_=cdet_.subs(ai_, 1)
            elif strechs[ai]==1:
                pass
            elif strechs[ai]==2:
                A=A*(1-ai_)
        

#        print cdet_ 
#        print det_
        
        res, ai_dict=diff_by_strechs(g_qi, model)
        (expr, vars)=symplify_expr(res, cdet_, det_, ai_dict)
        vars['U']=U*graph.sym_coef()
        vars['A ']=A
        eseries=[]
#        print vars
        
        for _expr in utils.series_lst(expr, e,  model.target-graph.NLoops()):
            eseries.append(term_func("func_%s_t%s"%(name, i), _expr, vars, ai_dict, g_qi._qi))
        func["func_%s_t%s"%(name, i)]=eseries
    
    
    return func

        
def save(name, graph_lst, model, overwrite=True):
    dirname = '%s/group_feynmanD/%s/'%(model.workdir,name)
    try:
        os.mkdir('%s/group_feynmanD'%model.workdir)
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
    func_total=dict()
    N_int=dict()
    for graph in graph_lst:
        Prepare(graph, model)
        print "det(v)=", graph._det_f
        print "det(v)*C = ", graph._cdet    
        e=sympy.var('e')
        cnt=0
        expr=0
        func=feynman_D_func(graph, model)
        func_total=utils.add_dicts(func_total, func)
    
        eps_cnt=0
        integrand=dict()
        N=nintegrations(graph, model)
        for f in func:
            N_int[f]=N
            
    print func_total.keys()    
    N=max(N_int.values())
    region=("0.,"*N+"1.,"*N)[:-1]

    main="void func (double k[DIMENSION], double f[FUNCTIONS])\n {\nf[0]=0.;\n"
    for f_series in func_total:
        for i in range(len(func_total[f_series])):
            f=func_total[f_series][i]
            if i not in integrand:
                integrand[i]="#define DIMENSION %s\n"%N+"#define FUNCTIONS 1\n"+"#define ITERATIONS 5\n" + "#define NTHREADS 2\n" +"#define NEPS 0\n"+"#define NITER 2\n" +  "double reg_initial[2*DIMENSION]={%s};\n"%region
            integrand[i]+=f
        args=""    
        for i in range(N_int[f_series]):
            args+="k[%s],"%i
        args=args[:-1]

        main+="f[0]+=%s(%s);\n"%(f_series, args)
    
    for eps_cnt in integrand.keys():
        integrand_=integrand[eps_cnt]
        f=open('%s/%s_E%s_O.c'%(dirname,name,eps_cnt),'w')
        f.write(calculate.core_pv_code(integrand_+main))
        f.close()
        eps_cnt+=1
         
                    

def compile(name,model):
    calculate.compile("group_feynmanD/%s/"%name, model)

def execute(name, model, points=10000, threads=4, calc_delta=0., neps=0):
    return calculate.execute("group_feynmanD/%s/"%name, model, points=points, threads=threads, calc_delta=calc_delta, neps=neps)

    

