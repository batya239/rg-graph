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

def Prepare(graph, model):
    name=str(graph.GenerateNickel())
    if name in ['e111-e-','ee11-22-ee-','ee11-23-e33-e-']:
        model.reduce=False
    model.SetTypes(graph)
    graph.FindSubgraphs(model)
    sym_coef=graph.sym_coef()
    graph=graph.ReduceSubgraphs(model)
    graph._sym_coef_orig=sym_coef
    graph.FindSubgraphs(model)
    print graph
    subs_toremove=subgraphs.DetectSauseges(graph._subgraphs)
    graph.RemoveSubgaphs(subs_toremove)

    print "moment index: ", moments.Generic(model, graph)

    utils.print_moments(graph._moments())
    print "subgraphs: ",graph._subgraphs_m


def save(name, graph, model, overwrite=True):
    dirname = '%s/graph/%s/momentumF/'%(model.workdir,name)
    try:
        os.mkdir(dirname)
    except:
        if overwrite:
            file_list = os.listdir(dirname)
            for file in file_list:
                if fnmatch.fnmatch(file,"*.c") or fnmatch.fnmatch(file,"*.run"):
                    os.remove(dirname+file)
                    
    Prepare(graph, model)

    jakob,subsvars = roperation.subs_vars(graph)
    cnt=0
    d,e=sympy.var('d e')
    if "_nloops_orig" in graph.__dict__:
        _nloops_orig=graph._nloops_orig
    else:
        _nloops_orig=graph.NLoops()
    print "norm start"
    norm=utils.series_f(utils.norm(graph.NLoops(),model.space_dim-e)*graph.sym_coef(), e, model.target-_nloops_orig)
    print norm
    print utils.series_f(utils.norm(graph.NLoops(),model.space_dim-e), e, model.target-_nloops_orig), graph.sym_coef()
    for g in model.dTau(graph):
        roperation.strechMoments(g, model)
        print cnt, g
        det=roperation.det(g, model)
        #expr=(jakob*det*roperation.AvgByExtDir(roperation.expr(g,model))).subs(d, model.space_dim-e)
        expr=(norm*jakob*det*roperation.AvgByExtDir(roperation.expr(g,model))).subs(d, model.space_dim-e)
        strechs=roperation.find_strech_atoms(expr)
        eps_cnt=0


        for _expr in utils.series_lst(expr,e,model.target-_nloops_orig):
            integrand=roperation.export_subs_vars_pv(subsvars,strechs)
            integrand+= "\nf[0]=1.0e-38;\n"
            integrand+= "f[0]+=%s;\n"%sympy.printing.ccode(_expr)
            f=open('%s/%s_E%s_%s.c'%(dirname,name,eps_cnt,cnt),'w')
            f.write(calculate.core_pv_code(integrand))
            f.close()
            eps_cnt+=1
        cnt+=1  
        
def compile(name,model):
    calculate.compile("%s/momentumF"%name, model)

def execute(name, model, points=10000, threads=2, calc_delta=0., neps=0):
    return calculate.execute("%s/momentumF"%name, model, points=points, threads=threads, calc_delta=calc_delta, neps=neps)        
    
def result(model, method):
    return calculate.result(model, method)
    
