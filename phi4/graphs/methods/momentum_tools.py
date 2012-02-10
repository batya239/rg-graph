#!/usr/bin/python

import roperation
import sympy
import utils
from sympy import Symbol
import re as regex


def find_independent(subs_vars, strechs):
    atomset=set()
    res=""
    for expr in subs_vars.values():
        atomset=atomset|expr.atoms(Symbol)
    cnt=0
    for atom in atomset|strechs:
        if regex.match("^y\d*$",str(atom)) or regex.match("^z_\d+_\d+$",str(atom)) or regex.match("^a_\d+.*$",str(atom))or regex.match("^u_\d+.*$",str(atom)):
            res=res+"double %s = k_%s;\n"%(atom,cnt)
            cnt+=1
    return res, cnt
        
            
def export_subs_vars_pv(subs_vars, strechs):
    def sort_vars(var_list):
        vars_=('u','c','s','q','a')
        dict_={}
        for var in vars_:
            dict_[var]=[]
        for var in var_list:
            for var_ in vars_:
                if regex.match('^%s.*'%var_,var):
                    dict_[var_].append(var)
        for var in vars_:
            (dict_[var]).sort()
        res=[]
        for var in vars_:
            res=res+dict_[var]
        return res
        
    res, n = find_independent(subs_vars, strechs)


#    res="#define DIMENSION %s\n"%cnt+"#define FUNCTIONS 1\n"+"#define ITERATIONS 5\n" + "#define NTHREADS 2\n" +"#define NEPS 0\n"+"#define NITER 2\n" +  "double reg_initial[2*DIMENSION]={%s};\nvoid func (double k[DIMENSION], double f[FUNCTIONS])\n {\n"%region+res

    for var in sort_vars(subs_vars.keys()):
        res=res + "double %s = %s;\n"%(var, sympy.printing.ccode(subs_vars[var]))
    return res

def term_func(name, expr, subsvars, strechs, n):
    args=""
    for i in range(n):
        args+=" double k_%s,"%i
    args=args[:-1]
    integrand="double %s(%s){%s"%(name,args,  export_subs_vars_pv(subsvars,strechs))
    integrand+= "\n double f=%s;\n return f;\n}\n"%sympy.printing.ccode(expr)
    
    return integrand
            
def momentumF_func(graph, model):
    jakob,subsvars = graph._jakob, graph._subsvars
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


    func=dict()
    cnt=0
    n_strechs=roperation.strechMoments(graph.Clone(), model)
    for g in model.dTau(graph):
        roperation.strechMoments(g, model)
        print cnt
        det=roperation.det(g, model)
#        print roperation.AvgByExtDir(roperation.expr(g,model))
        expr=(norm*jakob*det*roperation.AvgByExtDir(roperation.expr(g,model))).subs(d, model.space_dim-e)
#        print expr
        strechs=roperation.find_strech_atoms(expr)
        
        eseries=[]
        
        for _expr in utils.series_lst(expr,e,model.target-_nloops_orig):
            eseries.append(term_func("func%s"%cnt, _expr, subsvars, strechs, graph._n_int ))
#            print
#            print _expr
#            print
        func["func%s"%cnt]=eseries
        cnt+=1
    return func
    
def nintegrations(graph, model):
    n_strechs=roperation.strechMoments(graph.Clone(), model)
    res, n = find_independent(graph._subsvars, set())
    print n, n_strechs
    return n+n_strechs
