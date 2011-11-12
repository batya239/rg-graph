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

def symplify_expr(expr, C, D, ai_dict):
    vars=dict()
    print "C=", C
    print "D=", D
    vars['C']=C
    vars['D']=D
    for atom in expr.atoms(sympy.Symbol):
        satom=str(atom)
        print satom,  satom not in vars, vars.keys()
        var=None
        if satom not in vars:
            if regex.match('^C_.*', satom):
                var=C
            elif regex.match('^D_.*', satom):
                var=D
        
        if var<>None:
            diffs=satom.split('_')[1:]
            
            dvar=var
            for d in diffs:
                d_=sympy.var(ai_dict[d])
                dvar=dvar.diff(d_)
            print satom
            vars[satom]=dvar
    res=expr
    to_remove=[]
    for svar in vars:
        if vars[svar]==0:
            svar_=sympy.var(svar)
            res=res.subs(svar_, 0)
            to_remove.append(svar)
    for svar in to_remove:
        del vars[svar]
    return (res,  vars)
    
            
def diff_by_strechs(graph, model):
    strechs_orig=strech_indexes(graph, model)
    e, D, C, U, A=sympy.var('e D C U A')
    res=A*U/D**(2.-e/2.)
    if len(graph.ExternalLines())==2:
        res=res*C/D
    t=time.time()
    ai_dict=dict()
    for ai in strechs_orig:        
        ai__=sympy.var('a%s'%strechs_orig.keys().index(ai))
        ai_dict[str(ai__)]=str(ai)
        if strechs_orig[ai]==1:
            res=diff(res, ai__, exclude=['^e$', '^A.*', '^U.*'])
        elif strechs_orig[ai]==2:
            res=diff(diff(res, ai__, exclude=['^e$', '^A.*', '^U.*']), ai__, exclude=['^e$', '^A.*', '^U.*'])
        else:
            raise ValueError,  " invalid strech count %s -> %s"%(ai, strech_orig[ai])
    print t-time.time()
    print
    print res
    print

    return res, ai_dict

def usubs(n):
    """ part form feynman.subs_vars
    """
    u_last = 'double u_%s=1'%(n-1)
    factor = 'double factor=1.'
    res=""
    for i in range(n-1):
        u_str="double u_%s="%i
        for j in range(i):
            u_str+='w_%s*'%j
        if i<>n-2:
            u_str+='(1-w_%s);\n'%i
        else:
            u_str+='w_%s;\n'%i
        res+=u_str
        
        u_last+='-u_%s'%i
        if n-i-2>1:
            factor+='*pow(w_%s,%s)'%(i, n-2-i)
        elif n-i-2==1:
            factor+='*w_%s'%i
            
    res+="%s;\n%s;\n"%(u_last, factor)
    return res
            
            
def term_func(name, expr, subs, ai_dict, qi):
    wi=['w_%s'%i for i in range(len(qi)-1)]
    vars=""
    for var in wi+ai_dict.values():
        vars+=" double %s,"%var
    vars=vars[:-1]
    usubs_=usubs(len(qi))
    
    subs_=""
    for sub in subs:
        subs_+="double %s = %s;\n"%(sub, ccode(subs[sub]))
        
    c_expr="double res = factor*(%s);"%ccode(expr)
    res="double %s(%s)\n{\n%s\n%s\n%s\n return res;\n}\n"%(name, vars, usubs_, subs_, c_expr)
    return res
    
def feynman_D_func(graph, model):
    
    det=graph._det_f
    cdet=graph._cdet
    
    func=dict()
    
    for i in range(len(graph._qi.keys())):
        qi = graph._qi.keys()[i]
        g_qi=dTau_line(graph, qi,  model)
        strechs=strech_indexes(g_qi, model)
        
        U=sympy.Number(1.)
        
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
        
        print i
        print cdet_ 
        print det_
        
        res, ai_dict=diff_by_strechs(g_qi, model)
        (expr, vars)=symplify_expr(res, cdet_, det_, ai_dict)
        vars['U']=U*graph.sym_coef()
        vars['A ']=A
        eseries=[]
        print vars
        
        for _expr in utils.series_lst(expr, e,  model.target-graph.NLoops()):
            eseries.append(term_func("func%s"%i, _expr, vars, ai_dict, g_qi._qi))
        func["func%s"%i]=eseries
    
    
    return func

def nintegrations(graph, model):
    n=len(graph._qi)-1+len(strech_indexes(graph, model))
    return n
        
def save(name, graph, model, overwrite=True):
    dirname = '%s/%s/feynmanD/'%(model.workdir,name)
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
    func=feynman_D_func(graph, model)
#    for f in func:
#        for f1 in func[f]:
#            print  f1
#            print   
#        print
#    for qi in graph._qi:
#        expr+=feynman_term(graph, qi, model)
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
        f.write(calculate.core_pv_code(integrand_+main))
        f.close()
        eps_cnt+=1
         
                    

def compile(name,model):
    calculate.compile("%s/feynmanD"%name, model)

def execute(name, model, points=10000, threads=4, calc_delta=0., neps=0):
    return calculate.execute("%s/feynmanD"%name, model, points=points, threads=threads, calc_delta=calc_delta, neps=neps)

    

