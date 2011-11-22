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

        
        
def save(name, graph, model, overwrite=True):
    dirname = '%s/feynmanO/%s/'%(model.workdir,name)
    try:
        os.mkdir('%s/feynmanO/'%model.workdir)
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
    calculate.compile("feynmanO/%s/"%name, model)

def execute(name, model, points=10000, threads=2, calc_delta=0., neps=0):
    return calculate.execute("feynmanO/%s/"%name, model, points=points, threads=threads, calc_delta=calc_delta, neps=neps)
    

