#!/usr/bin/python
# -*- coding: utf8
'''
Created on Feb 17, 2010

@author: mkompan

definition of phi3 model in terms of rggraph_static
'''

import sympy
import os
import rggraph_static as rggrf
import copy

#definitions of propagators, node factors, dot actions, and K operation 

def propagator(**kwargs):
    tau=sympy.var('tau')
    momenta = kwargs["momenta"]
    return 1 / (momenta.Squared() + tau)

def external_node_factor(**kwargs):
    return rggrf.roperation.Factorized(1, 1)

def triple_node_factor(r1term,**kwargs):
    return rggrf.roperation.Factorized(1, 1)

def double_node_factor(r1term,**kwargs):
    squared_momenta = kwargs["moment0"].Squared()
    return rggrf.roperation.Factorized(1, squared_momenta)

def dot_action(**kwargs):
    tau = sympy.var('tau')
    propagator=kwargs["propagator"]
    return propagator.diff(tau)

def FindExtMomentAtoms(G):
    res=set(list())
    for ext_line in G.external_lines:
        res=res | set(ext_line.moments.dict.keys())
    return list(res)



def ExpandScalarProdsAndPrepareFactorized(factorized_expr,debug=False):
    return rggrf.roperation.Factorized(ExpandScalarProdsAndPrepare(factorized_expr.factor,debug), 
                      ExpandScalarProdsAndPrepare(factorized_expr.other,debug))

def ExpandScalarProdsAndPrepare(expr_,debug=False):
    if isinstance(expr_,rggrf.roperation.Factorized):
        rggrf.utils.print_debug( "WARNING!!! Factorizied object passed to ExpandScalarProdsAndPrepare",debug)
        expr = expr_.factor*expr_.other
    else:
        expr = expr_ 
    import re as regex
    try:
        atoms = expr.atoms()
    except:
        rggrf.utils.print_debug( "WARNING!!!! %s passed to ExpandScalarProdsAndPrepare" %type(expr),debug)
        return expr
    t_expr = expr
    for atom in atoms:
        reg = regex.match("^(.+)x(.+)$",str(atom))
        if reg :
            atom1 = sympy.var(reg.groups()[0])
            atom2 = sympy.var(reg.groups()[1])
            t_expr = t_expr.subs(atom,atom*atom1*atom2)
    #Prepare p=1, tau=1
    p=sympy.var('p')
    tau=sympy.var('tau')
    t_expr = t_expr.subs(p,1).subs(tau,1)
    return t_expr            

def FindLinesWithAtoms(G,atoms):
    lines_list=list()
    for idxL in G.intenal_lines:
        if len(set(atoms) & set(G.lines[idxL].momenta.dict.keys()))>0:
            lines_list.append(idxL)
    return lines_list

def K_n(G, diff_list=[]):
    diffs=list()
    ext_moment_atoms = FindExtMomentAtoms(G)
    if len(ext_moment_atoms)==1:
        for ext_diff in diff_list:
            cur_diff=dict()
            for idxL in ext_diff:
                if idxL not in cur_diff:
                    cur_diff[idxL]=list()
                cur_diff[idxL].append(ext_moment_atoms[0])
            diffs.append(cur_diff)                        
    elif len(diff_list)<>0:
        raise ValueError, "Non empty diff_list and no|complex external momenta"
    
#sub_diffs=dict()    
    for idxS in range(len(G.subgraphs)):
        subgraph = G.subgraphs[idxS]
        sub_ext_atoms = FindExtMomentAtoms(subgraph)
        strech_var_str = "a"
        int_lines = list(subgraph.internal_lines)
        int_lines.sort()
        for idxL in int_lines:
            strech_var_str = strech_var_str + "_%s"%idxL
        
        sub_ext_path = FindLinesWithAtoms(subgraph, sub_ext_atoms) 
        for idxL in sub_ext_path:
            line = G.Lines[idxL]
            if 'strech' not in line.__dict__:
                line.strech=dict()    
            line.strech[strech_var_str]=1

        if subgraph.dim >=0:
            degree = subgraph.dim+1
        else:
            raise ValueError, "irrelevant graph!!"
        sub_diffs = [i for i in rggrf.utils.xSelections(sub_ext_path,degree)]
        new_diffs=list()
        for cur_diff in diffs:
            for cur_sub_diff in sub_diffs:
                new_diff=copy.deepcopy(cur_diff)
                for idxL in cur_sub_diff:
                    if idxL not in new_diff:
                        new_diff[idxL]=list()
                    new_diff[idxL].append(strech_var_str)
                new_diffs.append(new_diff)
        diffs = new_diffs
    print diffs

        
    
           
# model initialization
model=rggrf.Model("phi3R")

# definition of line types (1 line type)
model.AddLineType(1, propagator=propagator, directed=0)

# definition of node types

#External Node always have number 0 and no Lines requirement
model.AddNodeType(0, Lines=[], Factor=external_node_factor,
                 gv={"color": "red"}) 
# phi3 node
model.AddNodeType(1, Lines=[1, 1, 1], Factor=triple_node_factor)

# nodes from Sigma subgraphs inf counterterms graphs
model.AddNodeType(2, Lines=[1, 1], Factor=double_node_factor)

# Nodes with K operation (Lines definition should much to one of 
# subgraphs definitions)

#TODO: generate such nodes automatically when adding subgraph types 
#phi3.AddNodeType(3, Lines=[1, 1, 1], Factor=K, gv={"color": "blue"})
#phi3.AddNodeType(4, Lines=[1, 1], Factor=K, gv={"color": "blue"})

# relevant subgraph types
model.AddSubGraphType(1, Lines=[1, 1, 1], dim=0, K_nodetypeR1=3)
model.AddSubGraphType(2, Lines=[1, 1], dim=2, K_nodetypeR1=4)

# definition of dots
model.AddDotType(1, dim=2, action=dot_action, gv={"penwidth":"3"})

model.basepath = rggrf.storage.filesystem.NormalizeBaseName("~/work/rg-graph/testR/")

try:
    os.listdir(rggrf.storage.filesystem.NormalizeBaseName(model.basepath))
except:
    raise ValueError, "invalid storage path  %s" %model.basepath
model.SaveGraph = rggrf.storage.filesystem.SaveGraphAsDict
model.LoadGraph = rggrf.storage.filesystem.LoadGraphAsDict

model.SaveResults = rggrf.storage.filesystem.SaveResults
model.LoadResults = rggrf.storage.filesystem.LoadResults

model.GetGraphList = rggrf.storage.filesystem.GetGraphList
model.WorkDir = rggrf.storage.filesystem.ChangeToWorkDir

model.target = 4

model.methods = dict()


def MCO_fstrvars(G, debug=False):
    G.GenerateNickel()
    base_name = "fstrvars_%s"%str(G.nickel)
    n_epsilon_series =G.model.target -G.NLoops()
    NPOINTS = 10000
    NTHREADS = 2
    SPACE_DIM = 6.
    prepared_eqs = []
    for idxL in G.internal_lines:
        
        rggrf.utils.print_debug("======= %s ======="%idxL, debug)
        cur_G = G.Clone()
        cur_G.lines[idxL].dots[1] = 1
        cur_G.DefineNodes()
        cur_G.FindSubgraphs()
        cur_r1 = rggrf.roperation.R1(cur_G)
#        cur_r1.SaveAsPNG("test.png")
    
        if len(G.external_lines) == 2:
            K2res = K2(cur_r1)
            for idxK2 in range(len(K2res)):
                k2term = K2res[idxK2]  
                s_prep =   ExpandScalarProdsAndPrepareFactorized(k2term,debug)
                rggrf.utils.print_debug( "---------dm_%s_p%s --------- " %(idxL,idxK2), debug)
                prepared_eqs.append(rggrf.integration.PrepareFactorizedStrVars(s_prep, SPACE_DIM, simplify=True, debug=debug))
       
        elif len(G.external_lines) == 3:
            K0res = K0(cur_r1) 
            s_prep =   ExpandScalarProdsAndPrepareFactorized(K0res)
            prepared_eqs.append(rggrf.integration.PrepareFactorizedStrVars(s_prep, SPACE_DIM, simplify=True, debug=debug))      
            
        sys.stdout.flush()
          
    prog_names = rggrf.integration.GenerateMCCodeForGraphStrVars(base_name, prepared_eqs,SPACE_DIM, n_epsilon_series, NPOINTS, NTHREADS,debug=debug) 
    
    t_res = rggrf.integration.CalculateEpsilonSeries(prog_names, build=True,debug=debug)
    (G.r1_dot_gamma, G.r1_dot_gamma_err) = ResultWithSd(t_res, G.NLoops(), n_epsilon_series)
    
    rggrf.utils.print_debug(str(G.r1_dot_gamma), debug)
    G.npoints = NPOINTS 
    G.method = "MCO_fstrvars"
    G.SaveResults()


model.methods['MCO_fstrvars'] = MCO_fstrvars



    
    
    
    
def ResultWithSd(_dict, nloops, n_eps_series):
    def RelativeError(expr, err, var):
        t_expr = expr
        t_err = err
        res = dict()
        idx = 0
        while(t_expr<>0):
            res[idx] = (t_err.subs(var,0),t_err.subs(var,0)/t_expr.subs(var,0))
            idx = idx + 1
            t_expr = t_expr.diff(var)/idx
            t_err = t_err.diff(var)/idx
        return res
    
    
    eps = var('eps')
    t_mnog=[1, 
            Real('0.84882636315677518', prec=15) - Real('0.093212888565618754', prec=15)*eps
            - Real('0.0050067349361000383', prec=15)*pow(eps,2) - 
            Real('0.00052717817355572589', prec=15)*pow(eps,3) - Real('6.8133402095973142e-5', prec=15)*pow(eps,4),
            Real('0.54037964609246814', prec=15) - Real('0.19443607942348598', prec=15)*eps 
            + Real('0.011647905519767411', prec=15)*pow(eps,2) + Real('0.00046123456498500229', prec=15)*pow(eps,3) + Real('4.052794127858356e-5', prec=15)*pow(eps,4),
            Real('0.21900762143326583', prec=15) - Real('0.17585458479914437', prec=15)*eps
            + Real('0.04636648202336683', prec=15)*pow(eps,2) - Real('0.0040301692384473609', prec=15)*pow(eps,3) + Real('3.08374601549584e-7', prec=15)*pow(eps,4),
            Real('0.044380222860623028', prec=15) - Real('0.068920756507029612', prec=15)*eps + Real('0.041670033558627036', prec=15)*pow(eps,2) 
            - Real('0.012317991965140199', prec=15)*pow(eps,3) + Real('0.0017870514760215828', prec=15)*pow(eps,4)
            ]
    expr = 0
    err = 0
    for idx in _dict:
        expr = expr + eps**idx*_dict[idx][0]
        err = err + eps**idx*_dict[idx][1]
    expr = rggrf.utils.SimpleSeries(expr * t_mnog[nloops-1], eps, 0, n_eps_series)
    err = rggrf.utils.SimpleSeries(err * t_mnog[nloops-1], eps, 0, n_eps_series)
    #print series(expr,eps,0)
    return (expr, RelativeError(expr, err, eps))

def ResultOldNotation(_dict):
    eps = var('eps')
    expr = 0
    for idx in _dict:
        expr = expr + eps**idx*_dict[idx][0]
     
    #print series(expr,eps,0)
    return expr*2