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

def AddStrech(Obj,strech, atoms_str):
    if isinstance(Obj,(rggrf.Line,rggrf.Node)):
        if 'strechs' not in Obj.__dict__:
            Obj.strechs=dict()   
        if strech not in Obj.strechs: 
            Obj.strechs[strech]=atoms_str
        else:
            raise ValueError, "Strech variable %s allready present in object"%strech
    else:
        raise NotImplementedError, "Do not know how to strech object: %s"%type(Obj)    

def AddDiff(Obj,var):
    if isinstance(Obj,(rggrf.Line,rggrf.Node)):
        if 'diffs' not in Obj.__dict__:
            Obj.diffs=list()   
        Obj.diffs.append(var)
    else:
        raise NotImplementedError, "Do not know how to diff object: %s"%type(Obj) 

def propagator(Line):
    tau=sympy.var('tau')
    res = 1 / (Line.momenta.Squared() + tau)
    if 'strechs' in Line.__dict__:
        for strech in Line.strechs:
            res = rggrf.StrechAtoms(res, Line.strechs[strech], strech, ignore_present_strech = False)
    if 'diffs' in Line.__dict__:
        for diff in Line.diffs:
            res = res.diff(sympy.var(diff))
    for idxD in Line.dots:
        for idx in range(Line.dots[idxD]):
            res = Line.model.dot_types[idxD]["action"](propagator=res)
    return res

def node_factor(Node):
    if Node.type == 0:
        res = rggrf.roperation.Factorized(1, 1) 
    elif Node.type == 1:
        res = rggrf.roperation.Factorized(1, 1)
    elif Node.type == 2:
        moment = Node.lines_dict.values()[0].momenta
        res = rggrf.roperation.Factorized(1, moment.Squared())
    else:
        raise ValueError, "Invalid node type: %s " %Node.type
    if 'strechs' in Node.__dict__:
        for strech in Node.strechs:
            res = rggrf.StrechAtoms(res, Node.strechs[strech], strech, ignore_present_strech = False)
    if 'diffs' in Node.__dict__:
        for diff in Node.diffs:
            res = rggrf.roperation.Factorized(1, (res.factor*res.other).diff(sympy.var(diff)))
    if 'dots' in Node.__dict__:
        for idxD in Node.dots:
            for idx in range(Node.dots[idxD]):
                res = rggrf.roperation.Factorized(1, Node.model.dot_types[idxD]["action"](propagator=res.factor*res.other))
    return res

def moment_serialize(Moment, preserve_sign=False):
    t_moment=Moment
    atoms = t_moment.dict.keys()
    atoms.sort()
    
    if not preserve_sign and Moment.dict[atoms[0]] <0:
        t_moment= -t_moment
        atoms = t_moment.dict.keys()
        atoms.sort()
    res = ""
    for atom in atoms:
        res = res + str((atom, t_moment.dict[atom]))
    return res

def strech_serialize(strechs):
    res = ""
    keys = strechs.keys()
    keys.sort()
    for key in keys:
        vars = strechs[key]
        vars.sort()
        res = res + str((key,vars))
    return res

def diff_serialize(diffs):
    
    import copy
    keys = copy.copy(diffs)
    keys.sort()
    return str(keys)

def dot_serialize(dots):
    res = ""
    for dot in dots:
        res = res + str(("dot%s"%dot, dots[dot]))
    return res

def line_serialize(Line): 
    s_moment = "moment:(%s)"%moment_serialize(Line.momenta, preserve_sign=False)
    
    if "strechs" in Line.__dict__:
        s_strechs = "strechs:(%s)"%strech_serialize(Line.strechs)
    else:
        s_strechs = "strechs:()"
        
    if "diffs" in Line.__dict__:
        s_diffs = "diffs:(%s)"%diff_serialize(Line.diffs)
    else:
        s_diffs = "diffs:()"
    
    s_dots = "dots:(%s)"%dot_serialize(Line.dots)
    
    return "line%s(%s,%s,%s,%s)"%(Line.type,s_moment,s_strechs,s_diffs,s_dots)

def node_serialize(Node):
    if Node.type == 0:
        s_moment = "" 
    elif Node.type == 1:
        s_moment = ""
    elif Node.type == 2:
        s_moment = moment_serialize(Node.lines_dict.values()[0].momenta, preserve_sign=False)
    else:
        raise ValueError, "Invalid node type: %s " %Node.type
    if "strechs" in Node.__dict__:
        s_strechs = "strechs:(%s)"%strech_serialize(Node.strechs)
    else:
        s_strechs = "strechs:()"
        
    if "diffs" in Node.__dict__:
        s_diffs = "diffs:(%s)"%diff_serialize(Node.diffs)
    else:
        s_diffs = "diffs:()"
    
    #s_dots = "dots:(%s)"%dot_serialize(Node.dots)
    
    return "node%s(%s,%s,%s)"%(Node.type,s_moment,s_strechs,s_diffs)

def graph_serialize(G):
    s_graph_dict=dict()
    for idxL in G.internal_lines:
        s_line=line_serialize(G.lines[idxL])
        if s_line in s_graph_dict.keys():
            s_graph_dict[s_line] =  s_graph_dict[s_line] + 1
        else:
            s_graph_dict[s_line] = 1
            
    for idxN in G.internal_nodes:
        s_node=node_serialize(G.nodes[idxN])
        if s_node in s_graph_dict.keys():
            s_graph_dict[s_node] =  s_graph_dict[s_node] + 1
        else:
            s_graph_dict[s_node] = 1
    
    keys = s_graph_dict.keys()
    keys.sort()
    
    res= ""
    for key in keys:
        res = res + str ((key, s_graph_dict[key]))
    
    return res
        
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

def compare_graphs(graph1,graph2):
    if len(graph1.internal_lines) < len(graph2.internal_lines):
        return 1
    elif len(graph1.internal_lines) == len(graph2.internal_lines):
        return 0
    else: 
        return -1

def subgraph_dim_with_diff(G,subgraph):
    dim = subgraph.dim
    for idxL in subgraph.internal_lines:
        if "diffs" in  G.lines[idxL].__dict__:
            dim = dim  - len(G.lines[idxL].diffs)
    for idxN in subgraph.internal_nodes:
        if "diffs" in  G.nodes[idxN].__dict__:
            dim = dim  - len(G.nodes[idxN].diffs)
    return dim

def checkdim_and_sort_subgraphs(G):
    res = list()
    for subgraph in G.subgraphs:
#        print "sub:%s,dim1:%s,dim2:%s\n"%(subgraph.internal_lines,subgraph.dim, subgraph_dim_with_diff(subgraph))
        
        dim = subgraph_dim_with_diff(G,subgraph)
        if dim >= 0:
            res.append(subgraph)
    res.sort(compare_graphs)
    return res
            
    


def K_nR1(G, N, Kres=dict(), debug=False):
    debug_level = 1
    ext_strech_var_str=None
#generate diffs for external moment, and appropriate strechs
    if N==0:
        diffs=[None,]
        extra_diff_multiplier = 1.
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
#                print idx,
                if idx[1]=="L":
                    obj = G.lines[idx[0]]
                elif idx[1]=="N":
                    obj = G.nodes[idx[0]]
                model.AddStrech(obj, ext_strech_var_str, ext_moment_atoms_str)
#                print obj.strechs
#                print
            diffs = [i for i in rggrf.utils.xSelections(ext_moment_path,N)]
                                    
        else:
            raise ValueError, "no or complex external momenta, atoms: %s"%ext_moment_atoms_str
    else:
        raise ValueError, " Unknown operation :  K%s"%N 
    G_list = list()
    for diff in diffs:
        cur_G=G.Clone()
        if diff == None:
            cur_G.extra_strech_multiplier=1.
            G_list.append(cur_G)
        else:
#            print
#            print diff
            for idx in diff:
                    if idx[1]=="L":
                        obj = cur_G.lines[idx[0]]
                    elif idx[1]=="N":
                        obj = cur_G.nodes[idx[0]]
                    model.AddDiff(obj, idx[2])
            cur_G.extra_strech_multiplier=1.
            cur_G.FindSubgraphs()
            #print diff,len(cur_G.subgraphs)
            G_list.append(cur_G)    

#generate diffs and strechs for subgraphs 

    
    stop = False
    new_G_list=G_list
    while (not stop):
        stop = True
        G_list=new_G_list
        new_G_list=list()
        for cur_G in G_list:
            cur_G.FindSubgraphs()
            subgraphs = checkdim_and_sort_subgraphs(cur_G)
            if debug:
                print 
                print "serial:", graph_serialize(cur_G)
                print "number of subgraphs:%s" %len(subgraphs)
                for sub in subgraphs:
                    print "sub %s, dim1:%s, dim2:%s"%(sub.internal_lines, sub.dim, subgraph_dim_with_diff(G, sub))
                    
            if len(subgraphs)>0:
                stop = False
                subgraph = subgraphs[0] 
                sub_ext_atoms_str = FindExtMomentAtoms(subgraph)
                strech_var_str = "a"
                int_lines = list(subgraph.internal_lines)
                int_lines.sort()
                for idxL in int_lines:
                    strech_var_str = strech_var_str + "_%s"%idxL
                sub_ext_path = [(i[0],i[1],strech_var_str) for i in FindExtMomentPath(subgraph, sub_ext_atoms_str)]
                for idx in sub_ext_path:
                    if idx[1]=="L":
                        obj = cur_G.lines[idx[0]]
                    elif idx[1]=="N":
                        obj = cur_G.nodes[idx[0]]
                    model.AddStrech(obj, strech_var_str, sub_ext_atoms_str)
                degree = subgraph_dim_with_diff(G, subgraph) +1    
                if degree<=0:
                    raise ValueError, "irrelevant graph!!"
                sub_diffs = [i for i in rggrf.utils.xSelections(sub_ext_path,degree)]
                strech_var = sympy.var(strech_var_str)
                if degree>1: 
                    cur_G.extra_strech_multiplier = cur_G.extra_strech_multiplier * (1.-strech_var)**(degree-1.)/sympy.factorial(degree-1)
                for diff in sub_diffs:
                    new_G=cur_G.Clone()
                    if diff == None:
                        raise ValueError, "diff can't be None" 
                    else:
                        
                        for idx in diff:
                            if idx[1]=="L":
                                obj = new_G.lines[idx[0]]
                            elif idx[1]=="N":
                                obj = new_G.nodes[idx[0]]
                            model.AddDiff(obj, idx[2])
                        new_G_list.append(new_G)
            else:
                new_G_list.append(cur_G)                 
                

    res_dict=Kres    
    for cur_G in G_list: 
        s_graph=graph_serialize(cur_G)
        if debug: 
            print
            print s_graph
            print
        
        if s_graph in res_dict.keys():
            res_dict[s_graph] = (res_dict[s_graph][0], res_dict[s_graph][1] + 1)
        else:
            t_res = rggrf.roperation.Factorized(1,extra_diff_multiplier*cur_G.extra_strech_multiplier)
#            print t_res.other
            for idxL in cur_G.internal_lines:
                curline=cur_G.lines[idxL]
                prop = curline.Propagator()
                if debug and debug_level > 0:
                    print "Line %s: "%idxL
                    sympy.pretty_print(prop)
                    
                t_res.other = t_res.other * prop
            
            for idxN in cur_G.internal_nodes:
                curnode = cur_G.nodes[idxN]
                
                factor = curnode.Factor()
                
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

            res_dict[s_graph]=(t_res, 1)
#    res=list()
#    for key in res_dict:
#        (t_res,t_cnt) = res_dict[key]
#        res.append(t_res*rggrf.roperation.Factorized(1,t_cnt))    
#    print
#    print len(res)
#    print

    if debug:
        print
        for key in res_dict:
            print "key:%s\n expr:%s\nfactor:%s\n\n"%(key,res_dict[key][0].factor*res_dict[key][0].other,res_dict[key][1])

    return res_dict
            
        
        
            
        
    
def L_dot(G, progress=None,debug=False):
    if progress <>  None:
        (progressbar,maxprogress) = progress
        step = float(maxprogress)/len(G.internal_lines)
        cur_progress = progressbar.currval
    Kres=dict()
    for idxL in G.internal_lines:
        cur_G=G.Clone()
        cur_G.lines[idxL].dots[1] = 1
        cur_G.DefineNodes()
        cur_G.FindSubgraphs()
#        cur_r1.SaveAsPNG("test.png")
    
        if len(G.external_lines) == 2:
            Kres = K_nR1(cur_G, 2, Kres, debug)
        elif len(G.external_lines) == 3:
            Kres = K_nR1(cur_G, 0, Kres, debug)
        else:
            raise ValueError, "unknown graph type"
        progressbar.update(cur_progress+step)
        cur_progress = progressbar.currval
    res=list()
    for key in Kres.keys():
        (t_res,t_cnt) = Kres[key]
        res.append(t_res*rggrf.roperation.Factorized(1,t_cnt))        
    return res
    
            
           
# model initialization
model=rggrf.Model("phi3R1")

# definition of line types (1 line type)
model.AddLineType(1, propagator=propagator, directed=0, fields=["start","end","dots","momenta"])

# definition of node types

#External Node always have number 0 and no Lines requirement
model.AddNodeType(0, Lines=[], Factor=node_factor, gv={"color": "red"}) 
# phi3 node
model.AddNodeType(1, Lines=[1, 1, 1], Factor=node_factor)

# nodes from Sigma subgraphs inf counterterms graphs
model.AddNodeType(2, Lines=[1, 1], Factor=node_factor)

model.AddStrech=AddStrech
model.AddDiff=AddDiff

# relevant subgraph types
model.AddSubGraphType(1, Lines=[1, 1, 1], dim=0, K_nodetypeR1=3)
model.AddSubGraphType(2, Lines=[1, 1], dim=2, K_nodetypeR1=4)

# definition of dots
model.AddDotType(1, dim=2, action=dot_action, gv={"penwidth":"3"})

model.basepath = rggrf.storage.filesystem.NormalizeBaseName("~/work/rg-graph/testR1/")

try:
    os.listdir(rggrf.storage.filesystem.NormalizeBaseName(model.basepath))
except:
    raise ValueError, "invalid storage path  %s" %model.basepath
model.SaveGraphMethod = rggrf.storage.filesystem.SaveGraphAsPickle
model.LoadGraphMethod = rggrf.storage.filesystem.LoadGraphFromPickle

model.SaveResults = rggrf.storage.filesystem.SaveResults
model.LoadResults = rggrf.storage.filesystem.LoadResults

model.GetGraphList = rggrf.storage.filesystem.GetGraphList
model.WorkDir = rggrf.storage.filesystem.ChangeToWorkDir

model.target = 4

model.methods = dict()


def MCT_SV(G, debug=False):
    import progressbar
    G.GenerateNickel()
    G.method = "MCT_SV"
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
    Kres = L_dot(G,progress=(bar,25),debug=debug)
    progress=bar.currval
    step = 25./len(Kres)
    for idxK2 in range(len(Kres)):
            kterm = Kres[idxK2]  
            s_prep =   ExpandScalarProdsAndPrepareFactorized(kterm,debug)
            rggrf.utils.print_debug( "--------- %s --------- " %(idxK2), debug)
            prepared_eqs.append(rggrf.integration.PrepareFactorizedStrVars(s_prep, SPACE_DIM, 
                                                                           simplify=False, 
                                                                           debug=debug))
            progress = progress + step
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


model.methods['MCT_SV'] = MCT_SV

def MCO_SV(G, debug=False):
    import progressbar
    G.GenerateNickel()
    G.method = "MCO_SV"
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
    Kres = L_dot(G,progress=(bar,25),debug=debug)
    progress=bar.currval
    step = 25./len(Kres)
    for idxK2 in range(len(Kres)):
            kterm = Kres[idxK2]  
            s_prep =   ExpandScalarProdsAndPrepareFactorized(kterm,debug)
            rggrf.utils.print_debug( "--------- %s --------- " %(idxK2), debug)
            prepared_eqs.append(rggrf.integration.PrepareFactorizedStrVars(s_prep, SPACE_DIM, 
                                                                           simplify=False, 
                                                                           debug=debug))
            progress = progress + step
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


model.methods['MCO_SV'] = MCO_SV


def MCT_SVd(G, debug=False):
    import progressbar
    G.GenerateNickel()
    G.method = "MCT_SVd"
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
    
    Kres = L_dot(G,progress=(bar,25),debug=debug)
    progress=bar.currval
    step = 25./len(Kres)
    for idxK2 in range(len(Kres)):
            kterm = Kres[idxK2]  
            s_prep =   ExpandScalarProdsAndPrepareFactorized(kterm,debug)
            rggrf.utils.print_debug( "--------- %s --------- " %(idxK2), debug)
            prepared_eqs.append(rggrf.integration.PrepareFactorizedStrVars(s_prep, SPACE_DIM, 
                                                                           simplify=False, 
                                                                           debug=debug))
            progress = progress + step
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
                                                     progress=(bar,24.9),
                                                     calc_delta=0.)
    
    (G.r1_dot_gamma, err) = ResultWithSd(t_res, G.NLoops(), n_epsilon_series)
    G.r1_dot_gamma_err = rggrf.utils.RelativeError(G.r1_dot_gamma, err, 
                                                   sympy.var('eps'))
    
    rggrf.utils.print_debug(str(G.r1_dot_gamma), debug)
    G.npoints = NPOINTS 
    
    G.SaveResults()
    bar.finish()


model.methods['MCT_SVd'] = MCT_SVd

def MCO_SVd(G, debug=False):
    import progressbar
    G.GenerateNickel()
    G.method = "MCO_SVd"
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
    Kres = L_dot(G,progress=(bar,25),debug=debug)
    progress=bar.currval
    step = 25./len(Kres)
    for idxK2 in range(len(Kres)):
            kterm = Kres[idxK2]  
            s_prep =   ExpandScalarProdsAndPrepareFactorized(kterm,debug)
            rggrf.utils.print_debug( "--------- %s --------- " %(idxK2), debug)
            prepared_eqs.append(rggrf.integration.PrepareFactorizedStrVars(s_prep, SPACE_DIM, 
                                                                           simplify=False, 
                                                                           debug=debug))
            progress = progress + step
            bar.update(progress)
                   
    sys.stdout.flush()
          
    prog_names = rggrf.integration.GenerateMCCodeForGraphStrVars(base_name, prepared_eqs, 
                                                                SPACE_DIM, n_epsilon_series, 
                                                                NPOINTS, NTHREADS,
                                                                debug=debug, 
                                                                progress=(bar,25.),
                                                                MCCodeGenerator=rggrf.integration.SavePThreadsMCCodeDelta) 
    
    t_res = rggrf.integration.CalculateEpsilonSeries(prog_names, 
                                                     build=True, debug=debug, 
                                                     progress=(bar,24.9),
                                                     calc_delta=0.)
    
    (G.r1_dot_gamma, err) = ResultWithSd(t_res, G.NLoops(), n_epsilon_series)
    G.r1_dot_gamma_err = rggrf.utils.RelativeError(G.r1_dot_gamma, err, 
                                                   sympy.var('eps'))
    
    rggrf.utils.print_debug(str(G.r1_dot_gamma), debug)
    G.npoints = NPOINTS 
    
    G.SaveResults()
    bar.finish()


model.methods['MCO_SVd'] = MCO_SVd

    
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