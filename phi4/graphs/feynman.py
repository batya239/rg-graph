#!/usr/bin/python
# -*- coding:utf8

import sympy
from sympy import Symbol
import os
import re as regex
import fnmatch
import utils
import time
import subgraphs
import moments


from roperation import feynman_qi_lambda, feynman_B, decompose_B, SubsSquaresStrechs,  strechMoments
import calculate
import utils

def Prepare(graph, model):
    model.SetTypes(graph)

    model.checktadpoles=False
    
    graph.FindSubgraphs(model)

    subs_toremove=subgraphs.DetectSauseges(graph._subgraphs)
    graph.RemoveSubgaphs(subs_toremove)

    subgraphs.RemoveTadpoles(graph)
    

    print "moment index: ", moments.Generic(model, graph, level=10**6)

    utils.print_moments(graph._moments())
    print "subgraphs: ",graph._subgraphs

    strechMoments(graph, model, external_strech=False)
    
    
    (graph._qi, graph._qi2line)=feynman_qi_lambda(graph)
    print  "qi2line =",[(i, graph._qi2line.values()[i]) for i in range(len(graph._qi2line))]
    B=feynman_B(graph._qi)
    print 
    (c,b,v)=decompose_B(B)
    print v
    #t=time.time()    
    #det=v.det()
    #print time.time()-t
    t=time.time()
    det=utils.det(v)
    print "det calculation time: ", time.time()-t
    t=time.time()
    if v.shape==(1, 1):
        Cdet=(((b.transpose()*v.inverse_GE()*b)[0] -c*det)*det).expand()
    else:
        Cdet=((b.transpose()*v.adjugate()*b)[0] -c*det).expand()
    print "cdet calculation time: ", time.time()-t

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
            res[sub._strechvar]=0
        elif dim==0:
            res[sub._strechvar]=1
        elif dim==2:
            res[sub._strechvar]=2
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
        if strechs[ai]==0:
            res=res.subs(ai_, sympy.Number(1))
        elif strechs[ai]==1:
            res=res.diff(ai_)
        elif strechs[ai]==2:
            res=res.diff(ai_).diff(ai_)*(1-ai_)
            
#TODO: add gammas Gamma(1+ne/2)*Gamma(2-e/2)**n ??.
    return res
            

def subs_vars(expr):
    atoms=expr.atoms(Symbol)
    ulist=list()
    alist=list()
    for atom in atoms:
        satom=str(atom)
        if regex.match('^u_\d.*', satom):
            ulist.append(satom)
        elif regex.match('^a_\d.*', satom):
            alist.append(satom)
    cnt=0
    res=""
    u_last="double %s=1"%ulist[-1]
    factor="double factor=1."
    L=len(ulist)
    for u in ulist[:-1]:
        u_str="double %s="%u
        for i in range(cnt):
            u_str+="k[%s]*"%i
        if cnt<>L-2:
            u_str+="(1-k[%s]);\n"%cnt
        else:
            u_str+="k[%s];\n"%cnt
        res+=u_str
        
        u_last+="-%s"%u
        if L-2-cnt>1:
            factor+="*pow(k[%s],%s)"%(cnt, L-2-cnt)
        elif L-2-cnt==1:
            factor+="*k[%s]"%(cnt)
        
        cnt+=1
        

    u_last+=";\n"
    res+=u_last;
    
    for a in alist:
        res+="double %s=k[%s];\n"%(a,  cnt)
        cnt+=1
    
    res+=factor+";\n"
    
    region=("0.,"*cnt+"1.,"*cnt)[:-1]
    
    res="#define DIMENSION %s\n"%cnt+"#define FUNCTIONS 1\n"+"#define ITERATIONS 5\n" + "#define NTHREADS 2\n" +"#define NEPS 0\n"+"#define NITER 2\n" +  "double reg_initial[2*DIMENSION]={%s};\nvoid func (double k[DIMENSION], double f[FUNCTIONS])\n {\n"%region+res

    return res
    
        
        
def save(name, graph, model, overwrite=True):
    dirname = '%s/feynman/%s/'%(model.workdir,name)
    try:
        os.mkdir('%s/feynman'%model.workdir)
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
    print "det(v)=", graph._det_f
    print "det(v)*C = ", graph._cdet    
    e=sympy.var('e')
    cnt=0
    for qi in graph._qi:
        expr=feynman_term(graph, qi, model)
        eps_cnt=0
        for _expr in utils.series_lst(expr, e,  model.target - graph.NLoops()):
            integrand=subs_vars(_expr)
            integrand+= "\nf[0]=1.0e-38;\n"
            integrand+= "f[0]+=factor*(%s);\n"%( sympy.printing.ccode(_expr*graph.sym_coef()))
            f=open('%s/%s_E%s_%s.c'%(dirname,name,eps_cnt,cnt),'w')
            f.write(calculate.core_pv_code(integrand))
            f.close()
            eps_cnt+=1
        cnt+=1  
                    

def compile(name,model):
    calculate.compile("feynman/%s"%name, model)

def execute(name, model, points=10000, threads=2, calc_delta=0., neps=0):
    return calculate.execute("feynman/%s"%name, model, points=points, threads=threads, calc_delta=calc_delta, neps=neps)

def normalize(graph, result):
    (res_, err_)=result
    n=graph.NLoops()
    e=sympy.var('e')
    res=0.
    err=0.
    
    for i in range(len(res_)):
        res+=e**i*res_[i]
        err+=e**i*abs(err_[i])
    res=res*sympy.special.gamma_functions.gamma(1+n*e/2.)*sympy.special.gamma_functions.gamma(2-e/2.)**n/2**n
    err=err*sympy.special.gamma_functions.gamma(1+n*e/2.)*sympy.special.gamma_functions.gamma(2-e/2.)**n/2**n
    
    return ([float(i) for i in utils.series_lst(res, e,  len(res_)-1)], [float(i) for i in utils.series_lst(err, e,  len(res_)-1)])

def result(model, method, **kwargs):
    return calculate.result(model, method, **kwargs)

    
 
