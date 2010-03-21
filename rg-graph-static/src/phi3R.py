#!/usr/bin/python
# -*- coding: utf8
'''
Created on Feb 17, 2010

@author: mkompan

definition of phi3 model in terms of rggraph_static
'''

import sympy
import os
import sys
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
        res=res | set(G.lines[ext_line].momenta.dict.keys())
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
    for idxL in G.internal_lines:
        if len(set(atoms) & set(G.lines[idxL].momenta.dict.keys()))>0:
            lines_list.append(idxL)
    return lines_list

def FindExtMomentPath(G,atoms):
    ext_moment_path=list()
    path_lines=FindLinesWithAtoms(G,atoms)
    for line in path_lines:
        ext_moment_path.append((line,"L"))
        for node in G.lines[line].Nodes():
            if G.nodes[node].type == 2 and (node,"N") not in ext_moment_path:
                ext_moment_path.append((node,"N"))
    return ext_moment_path


def K_nR1(G, N, debug=False):
    debug_level = 1
    ext_strech_var_str=None
    if N==0:
        diffs=[None,]
        extra_diff_multiplier = 1
    elif N==2:
        extra_diff_multiplier = 0.5
        ext_moment_atoms_str = FindExtMomentAtoms(G)
        if len(ext_moment_atoms_str)==1:
            ext_strech_var_str = "%s_strech_var"%ext_moment_atoms_str[0]
            ext_moment_path = [(i[0],i[1],ext_strech_var_str) for i in FindExtMomentPath(G,ext_moment_atoms_str)]
            if debug and debug_level>0:
                print
                print ext_moment_path
                print
            for idx in ext_moment_path:
                if idx[1]=="L":
                    line = G.lines[idx[0]]
                    if 'strech' not in line.__dict__:
                        line.strech=dict()    
                    line.strech[ext_strech_var_str]=ext_moment_atoms_str
                elif idx[1]=="N":
                    node = G.nodes[idx[0]]
                    if 'strech' not in node.__dict__:
                        node.strech=dict()    
                    node.strech[ext_strech_var_str]=ext_moment_atoms_str
            diffs = [i for i in rggrf.utils.xSelections(ext_moment_path,N)]                        
        else:
            raise ValueError, "no or complex external momenta, atoms: %s"%ext_moment_atoms_str
    else:
        raise ValueError, " Unknown operation :  K%s"%N 

    extra_strech_multiplier=1.
#sub_diffs=dict()    
    for idxS in range(len(G.subgraphs)):
        subgraph = G.subgraphs[idxS]
        sub_ext_atoms_str = FindExtMomentAtoms(subgraph)
        strech_var_str = "a"
        int_lines = list(subgraph.internal_lines)
        int_lines.sort()
        for idxL in int_lines:
            strech_var_str = strech_var_str + "_%s"%idxL
        
        sub_ext_path = [(i[0],i[1],strech_var_str) for i in FindExtMomentPath(subgraph, sub_ext_atoms_str)] 
        
        for idx in sub_ext_path:
            if idx[1]=="L":
                line = G.lines[idx[0]]
                if 'strech' not in line.__dict__:
                    line.strech=dict()    
                line.strech[strech_var_str]=sub_ext_atoms_str
            elif idx[1]=="N":
                node = G.nodes[idx[0]]
                if 'strech' not in node.__dict__:
                    node.strech=dict()    
                node.strech[strech_var_str]=sub_ext_atoms_str

        if subgraph.dim >=0:
            degree = subgraph.dim+1
        else:
            raise ValueError, "irrelevant graph!!"
        sub_diffs = [i for i in rggrf.utils.xSelections(sub_ext_path,degree)]
        strech_var = sympy.var(strech_var_str)
        if degree>0: 
            extra_strech_multiplier = extra_strech_multiplier * (1.-strech_var)**(degree-1.)/sympy.factorial(degree-1) 
        new_diffs=list()
        for diff in diffs:
            if diff == None:
                cur_diff = list()
            else:
                cur_diff = diff
            #print cur_diff
            for cur_sub_diff in sub_diffs:
                new_diff=copy.deepcopy(cur_diff)
                for idx in cur_sub_diff:
                    new_diff.append(idx)
                new_diffs.append(new_diff)
        diffs = new_diffs
    if debug:    
        print diffs
    
    res=list()
    for diff in diffs:
        if diff == None:
            cur_diff = list()
        else:
            cur_diff = diff
        if debug:
            print "current diff: ",diff
                
        t_res = rggrf.roperation.Factorized(1,extra_diff_multiplier*extra_strech_multiplier)
        for idxL in G.internal_lines:
            curline=G.lines[idxL]
            prop = G.model.line_types[curline.type]["propagator"](momenta=curline.momenta)
            for idxD in curline.dots:
                for idx in range(curline.dots[idxD]):
                    prop = G.model.dot_types[idxD]["action"](propagator=prop)
            if "strech" in curline.__dict__:
                for cur_strech_str in curline.strech:
                    strech_atoms =[sympy.var(i) for i in curline.strech[cur_strech_str]]
                    strech_var = sympy.var(cur_strech_str)
                    for atom in strech_atoms:
                        prop = rggrf.Streching(prop, atom, strech_var, ignore_present_strech=True)
            for cur_cur_diff in cur_diff:
                if cur_cur_diff[0]==idxL and cur_cur_diff[1] == "L":
                    diff_var = sympy.var(cur_cur_diff[2])                        
                    prop = prop.diff(diff_var)
            if debug and debug_level > 0:
                print "Line %s: "%idxL
                sympy.pretty_print(prop)
                
            t_res.other = t_res.other * prop
        
        for idxN in G.internal_nodes:
            curnode = G.nodes[idxN]
            
            node_moments = dict()
            for idx in range(len(curnode.lines)):
                if G.lines[curnode.lines[idx]].end == idxN:
                    node_moments["moment%s"%idx] = G.lines[curnode.lines[idx]].momenta
                else:
                    node_moments["moment%s"%idx] = - G.lines[curnode.lines[idx]].momenta
                    
            factor = G.model.node_types[curnode.type]["Factor"](None, **node_moments)
            if "strech" in curnode.__dict__:
                if debug_level >0:
                    rggrf.utils.print_debug("node %s, strech: %s, factor: %s"%(idxN,curnode.strech,factor.factor), debug)
                for cur_strech_str in curnode.strech:
                    strech_atoms =[sympy.var(i) for i in curnode.strech[cur_strech_str]]
                    strech_var = sympy.var(cur_strech_str)
                    for atom in strech_atoms:
                        factor = rggrf.Streching(factor, atom, strech_var, ignore_present_strech=True)
            for cur_cur_diff in cur_diff:
                if cur_cur_diff[0]==idxN and cur_cur_diff[1] == "N":
                    diff_var = sympy.var(cur_cur_diff[2])
                    factor = rggrf.roperation.Factorized(1,(factor.factor*factor.other).diff(diff_var))
            if debug and debug_level > 0:
                print "Node %s: "%idxN
                sympy.pretty_print(factor.other*factor.factor)
            t_res = t_res * factor
        if ext_strech_var_str <>None:
            strech_var = sympy.var(ext_strech_var_str)
            try:
                atoms = t_res.factor.atoms()
            except:
                pass
            else:
                t_res.factor = t_res.factor.subs(strech_var,0)
            try:
                atoms = t_res.other.atoms()
            except:
                pass
            else:
                t_res.other = t_res.other.subs(strech_var,0)
        
        if debug:
            sympy.pretty_print(t_res.factor*t_res.other)
        res.append(t_res)
            
    return res
            
        
        
            
        
def K2R1(G, debug=False):
    
    if isinstance(G,rggrf.Graph):
        return K_nR1(G,2,debug)
    else:
        raise TypeError, "Invalid type" 

def K0R1(G,debug=False):
    
    if isinstance(G,rggrf.Graph):
        return K_nR1(G,0,debug)
    else:
        raise TypeError, "Invalid type" 

    
           
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


def MCT_fstrvars(G, debug=False):
    import progressbar
    G.GenerateNickel()
    G.method = "MCT_fstrvars"
    base_name = "%s_%s"%(G.method,str( G.nickel))
    n_epsilon_series =G.model.target -G.NLoops()
    NPOINTS = 10000
    NTHREADS = 2
    SPACE_DIM = 6.
    prepared_eqs = []
    bar = progressbar.ProgressBar(maxval=100, term_width=70, 
                                  widgets=["%s  "%G.nickel, progressbar.Percentage(), 
                                           " ", progressbar.Bar(), 
                                           progressbar.ETA()]).start()
    progress = 0
    step=50./len(G.internal_lines)
    for idxL in G.internal_lines:
        
        rggrf.utils.print_debug("======= %s ======="%idxL, debug)
        cur_G = G.Clone()
        cur_G.lines[idxL].dots[1] = 1
        cur_G.DefineNodes()
        cur_G.FindSubgraphs()
#        cur_r1.SaveAsPNG("test.png")
    
        if len(G.external_lines) == 2:
            Kres = K2R1(cur_G, debug)
        elif len(G.external_lines) == 3:
            Kres = K0R1(cur_G, debug)
        else:
            raise ValueError, "unknown graph type"
        substep = step/len(Kres)
        for idxK2 in range(len(Kres)):
                kterm = Kres[idxK2]  
                s_prep =   ExpandScalarProdsAndPrepareFactorized(kterm,debug)
                rggrf.utils.print_debug( "---------dm_%s_p%s --------- " %(idxL,idxK2), debug)
                prepared_eqs.append(rggrf.integration.PrepareFactorizedStrVars(s_prep, SPACE_DIM, 
                                                                               simplify=False, 
                                                                               debug=debug))
                progress = progress + substep
                bar.update(progress)
                   
        sys.stdout.flush()
          
    prog_names = rggrf.integration.GenerateMCCodeForTermStrVars(base_name, prepared_eqs, 
                                                                SPACE_DIM, n_epsilon_series, 
                                                                NPOINTS, NTHREADS,
                                                                debug=debug, 
                                                                progress=(bar,25.)) 
    
    t_res = rggrf.integration.CalculateEpsilonSeries(prog_names, 
                                                     build=True, debug=debug, 
                                                     progress=(bar,24.9))
    
    (G.r1_dot_gamma, err) = ResultWithSd(t_res, G.NLoops(), n_epsilon_series)
    G.r1_dot_gamma_err = rggrf.utils.RelativeError(G.r1_dot_gamma, err, 
                                                   sympy.var('eps'))
    
    rggrf.utils.print_debug(str(G.r1_dot_gamma), debug)
    G.npoints = NPOINTS 
    
    G.SaveResults()
    bar.finish()


model.methods['MCT_fstrvars'] = MCT_fstrvars

def MCO_fstrvars(G, debug=False):
    import progressbar
    G.GenerateNickel()
    G.method = "MCO_fstrvars"
    base_name = "%s_%s"%(G.method,str( G.nickel))
    n_epsilon_series =G.model.target -G.NLoops()
    NPOINTS = 10000
    NTHREADS = 2
    SPACE_DIM = 6.
    prepared_eqs = []
    bar = progressbar.ProgressBar(maxval=100, term_width=70, 
                                  widgets=["%s  "%G.nickel, progressbar.Percentage(), 
                                           " ", progressbar.Bar(), 
                                           progressbar.ETA()]).start()
    progress = 0
    step=50./len(G.internal_lines)
    for idxL in G.internal_lines:
        
        rggrf.utils.print_debug("======= %s ======="%idxL, debug)
        cur_G = G.Clone()
        cur_G.lines[idxL].dots[1] = 1
        cur_G.DefineNodes()
        cur_G.FindSubgraphs()
#        cur_r1.SaveAsPNG("test.png")
    
        if len(G.external_lines) == 2:
            Kres = K2R1(cur_G, debug)
        elif len(G.external_lines) == 3:
            Kres = K0R1(cur_G, debug)
        else:
            raise ValueError, "unknown graph type"
        substep = step/len(Kres)
        for idxK2 in range(len(Kres)):
                kterm = Kres[idxK2]  
                s_prep =   ExpandScalarProdsAndPrepareFactorized(kterm,debug)
                rggrf.utils.print_debug( "---------dm_%s_p%s --------- " %(idxL,idxK2), debug)
                prepared_eqs.append(rggrf.integration.PrepareFactorizedStrVars(s_prep, SPACE_DIM, 
                                                                               simplify=False, 
                                                                               debug=debug))
                progress = progress + substep
                bar.update(progress)
                   
        sys.stdout.flush()
          
    prog_names = rggrf.integration.GenerateMCCodeForGraphStrVars(base_name, prepared_eqs, 
                                                                SPACE_DIM, n_epsilon_series, 
                                                                NPOINTS, NTHREADS,
                                                                debug=debug, 
                                                                progress=(bar,25.)) 
    
    t_res = rggrf.integration.CalculateEpsilonSeries(prog_names, 
                                                     build=True, debug=debug, 
                                                     progress=(bar,24.9))
    
    (G.r1_dot_gamma, err) = ResultWithSd(t_res, G.NLoops(), n_epsilon_series)
    G.r1_dot_gamma_err = rggrf.utils.RelativeError(G.r1_dot_gamma, err, 
                                                   sympy.var('eps'))
    
    rggrf.utils.print_debug(str(G.r1_dot_gamma), debug)
    G.npoints = NPOINTS 
    
    G.SaveResults()
    bar.finish()


model.methods['MCO_fstrvars'] = MCO_fstrvars


def MCT_fstrvars_delta(G, debug=False):
    import progressbar
    G.GenerateNickel()
    G.method = "MCT_fstrvars_delta"
    base_name = "%s_%s"%(G.method,str( G.nickel))
    n_epsilon_series =G.model.target -G.NLoops()
    NPOINTS = 10000
    NTHREADS = 2
    SPACE_DIM = 6.
    prepared_eqs = []
    bar = progressbar.ProgressBar(maxval=100, term_width=70, 
                                  widgets=["%s  "%G.nickel, progressbar.Percentage(), 
                                           " ", progressbar.Bar(), 
                                           progressbar.ETA()]).start()
    progress = 0
    step=50./len(G.internal_lines)
    for idxL in G.internal_lines:
        
        rggrf.utils.print_debug("======= %s ======="%idxL, debug)
        cur_G = G.Clone()
        cur_G.lines[idxL].dots[1] = 1
        cur_G.DefineNodes()
        cur_G.FindSubgraphs()
#        cur_r1.SaveAsPNG("test.png")
    
        if len(G.external_lines) == 2:
            Kres = K2R1(cur_G, debug)
        elif len(G.external_lines) == 3:
            Kres = K0R1(cur_G, debug)
        else:
            raise ValueError, "unknown graph type"
        substep = step/len(Kres)
        for idxK2 in range(len(Kres)):
                kterm = Kres[idxK2]  
                s_prep =   ExpandScalarProdsAndPrepareFactorized(kterm,debug)
                rggrf.utils.print_debug( "---------dm_%s_p%s --------- " %(idxL,idxK2), debug)
                prepared_eqs.append(rggrf.integration.PrepareFactorizedStrVars(s_prep, SPACE_DIM, 
                                                                               simplify=False, 
                                                                               debug=debug))
                progress = progress + substep
                bar.update(progress)
                   
        sys.stdout.flush()
          
    prog_names = rggrf.integration.GenerateMCCodeForTermStrVars(base_name, prepared_eqs, 
                                                                SPACE_DIM, n_epsilon_series, 
                                                                NPOINTS, NTHREADS,
                                                                debug=debug, 
                                                                progress=(bar,25.),
                                                                MCCodeGenerator=rggrf.integration.SavePThreadsMCCodeDelta) 
    
    t_res = rggrf.integration.CalculateEpsilonSeries(prog_names, 
                                                     build=True, debug=debug, 
                                                     progress=(bar,24.9))
    
    (G.r1_dot_gamma, err) = ResultWithSd(t_res, G.NLoops(), n_epsilon_series)
    G.r1_dot_gamma_err = rggrf.utils.RelativeError(G.r1_dot_gamma, err, 
                                                   sympy.var('eps'))
    
    rggrf.utils.print_debug(str(G.r1_dot_gamma), debug)
    G.npoints = NPOINTS 
    
    G.SaveResults()
    bar.finish()


model.methods['MCT_fstrvars_delta'] = MCT_fstrvars_delta

    
def ResultWithSd(_dict, nloops, n_eps_series):
    
    eps = sympy.var('eps')
    t_mnog=[1, 
            sympy.Real('0.84882636315677518', prec=15) - sympy.Real('0.093212888565618754', prec=15)*eps
            - sympy.Real('0.0050067349361000383', prec=15)*pow(eps,2) - 
            sympy.Real('0.00052717817355572589', prec=15)*pow(eps,3) - 
            sympy.Real('6.8133402095973142e-5', prec=15)*pow(eps,4),
            sympy.Real('0.54037964609246814', prec=15) - sympy.Real('0.19443607942348598', prec=15)*eps 
            + sympy.Real('0.011647905519767411', prec=15)*pow(eps,2) + 
            sympy.Real('0.00046123456498500229', prec=15)*pow(eps,3) + 
            sympy.Real('4.052794127858356e-5', prec=15)*pow(eps,4),
            sympy.Real('0.21900762143326583', prec=15) - sympy.Real('0.17585458479914437', prec=15)*eps
            + sympy.Real('0.04636648202336683', prec=15)*pow(eps,2) - 
            sympy.Real('0.0040301692384473609', prec=15)*pow(eps,3) + 
            sympy.Real('3.08374601549584e-7', prec=15)*pow(eps,4),
            sympy.Real('0.044380222860623028', prec=15) - sympy.Real('0.068920756507029612', prec=15)*eps + 
            sympy.Real('0.041670033558627036', prec=15)*pow(eps,2) 
            - sympy.Real('0.012317991965140199', prec=15)*pow(eps,3) + 
            sympy.Real('0.0017870514760215828', prec=15)*pow(eps,4)
            ]
    expr = 0
    err = 0
    for idx in _dict:
        expr = expr + eps**idx*_dict[idx][0]
        err = err + eps**idx*_dict[idx][1]
    expr = rggrf.utils.SimpleSeries(expr * t_mnog[nloops-1], eps, 0, n_eps_series)
    err = rggrf.utils.SimpleSeries(err * t_mnog[nloops-1], eps, 0, n_eps_series)
    #print series(expr,eps,0)
    return (expr, err)

def ResultOldNotation(_dict):
    eps = sympy.var('eps')
    expr = 0
    for idx in _dict:
        expr = expr + eps**idx*_dict[idx][0]
     
    #print series(expr,eps,0)
    return expr*2