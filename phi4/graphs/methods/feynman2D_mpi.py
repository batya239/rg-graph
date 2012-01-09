#!/usr/bin/python
# -*- coding:utf8

import sympy
from sympy import Symbol
import os
import fnmatch
import utils

import calculate
import utils
import re as regex

from feynman2D import Prepare, feynman_D_func, nintegrations 

def save(name, graph, model, overwrite=True):
    dirname = '%s/feynman2D_mpi/%s/'%(model.workdir,name)
    try:
        os.mkdir('%s/feynman2D_mpi'%model.workdir)
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
                    
    Prepare(graph, model)
   
    e=sympy.var('e')
    cnt=0
    expr=0
    func=feynman_D_func(graph, model)

    eps_cnt=0
    integrand=dict()
    N=nintegrations(graph, model)
    region=("0.,"*N+"1.,"*N)[:-1]
    args=""
    for i in range(N):
        args+="k[%s],"%i
    args=args[:-1]
    main="void func (double k[DIMENSION], double f[FUNCTIONS])\n {\nf[0]=0.;\n"
    for f_series in func:
        for i in range(len(func[f_series])):
            f=func[f_series][i]
            if i not in integrand:
                integrand[i]="#define DIMENSION %s\n"%N+"#define FUNCTIONS 1\n"+"#define ITERATIONS 5\n" + "#define NTHREADS 2\n" +"#define NEPS 0\n"+"#define NITER 2\n" +  "double reg_initial[2*DIMENSION]={%s};\n"%region
            integrand[i]+=f
        main+="f[0]+=%s(%s);\n"%(f_series, args)
    
    for eps_cnt in integrand.keys():
        integrand_=integrand[eps_cnt]
        f=open('%s/%s_E%s_O.c'%(dirname,name,eps_cnt),'w')
        f.write(calculate.core_pvmpi_code(integrand_+main))
        f.close()
        eps_cnt+=1
         
                    

def compile(name,model):
    calculate.compile_mpi("feynman2D_mpi/%s/"%name, model)

def execute(name, model, points=10000, threads=4, calc_delta=0., neps=0):
    return calculate.execute_mpi("feynman2D_mpi/%s/"%name, model, points=points, threads=threads, calc_delta=calc_delta, neps=neps)

    

