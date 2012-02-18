#!/usr/bin/python
# -*- coding:utf8

import os
import sympy

import utils
import subgraphs
import calculate
import moments
import roperation
import fnmatch
import momentum_tools

method_name= "momentumF"
code_=calculate.core_pv_code
compile_=calculate.compile
execute_=calculate.execute

def Prepare(graph, model):
    name=str(graph.GenerateNickel())
    if name in ['e111-e-','ee11-22-ee-','ee11-23-e33-e-']:
        model.reduce=False
    model.SetTypes(graph)
    graph.FindSubgraphs(model)
    sym_coef=graph.sym_coef()
    graph1=graph.ReduceSubgraphs(model)
    graph1._sym_coef_orig=sym_coef
    graph1.FindSubgraphs(model)
    print graph
    print "reduced:", graph1
    subs_toremove=subgraphs.DetectSauseges(graph1._subgraphs)
    graph1.RemoveSubgaphs(subs_toremove)

    print graph1._subgraphs
    print "moment index: ", moments.Generic(model, graph1)

    utils.print_moments(graph1._moments())
    print "subgraphs: ",graph1._subgraphs_m
    graph1._jakob,graph1._subsvars = roperation.subs_vars(graph1) 
    return graph1

def save(name, graph, model, overwrite=True):
    dirname = '%s/%s/%s/'%(model.workdir,method_name, name)
    try:
        os.mkdir('%s/%s'%(model.workdir, method_name))
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
                    
    graph=Prepare(graph, model)

    graph._n_int=momentum_tools.nintegrations(graph, model)
    func=momentum_tools.momentumF_func(graph, model)
    
    integrand=dict()
    N=graph._n_int
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
        f.write(code_(integrand_+main))
        f.close()
        eps_cnt+=1
        
        
def compile(name,model):
    compile_("%s/%s/"%(method_name, name), model)

def execute(name, model, points=10000, threads=2, calc_delta=0., neps=0):
    return execute_("%s/%s/"%(method_name, name), model, points=points, threads=threads, calc_delta=calc_delta, neps=neps)        
    
def result(model, method):
    return calculate.result(model, method)
    
