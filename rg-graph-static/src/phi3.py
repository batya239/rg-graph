#!/usr/bin/python
# -*- coding: utf8
'''
Created on Feb 17, 2010

@author: mkompan

definition of phi3 model in terms of rggraph_static
'''
from sympy import *
import rggraph_static as rggrf

#definitions of propagators, node factors, dot actions, and K operation 

def propagator(**kwargs):
    tau=var('tau')
    momenta = kwargs["momenta"]
    return 1 / (momenta.Squared() + tau)

def external_node_factor(**kwargs):
    return 1

def triple_node_factor(r1term,**kwargs):
    return 1

def double_node_factor(r1term,**kwargs):
    squared_momenta = kwargs["momenta0"].Squared()
    return squared_momenta

def dot_action(**kwargs):
    tau = var('tau')
    propagator=kwargs["propagator"]
    return propagator.diff(tau)

def FindExtMomenta(G):
    if len(G.external_lines) <> 2:
        raise ValueError, "not self-energy subgraph"
    else:
#TODO: понять важен ли знак втекающего импульса?
        if G.lines[list(G.external_lines)[0]].end in G.internal_nodes :
            res = G.lines[list(G.external_lines)[0]].momenta
        else:
            res = - G.lines[list(G.external_lines)[0]].momenta
    return res

def FindFreeMomenta(G):
# TODO: rename function
    ext_nodes = set([])
    for idxL in G.external_lines:
        ext_nodes = ext_nodes | set(G.lines[idxL].Nodes())
    ext_nodes = ext_nodes & G.internal_nodes
    t_list = list(ext_nodes)
    t_list.sort()
    res = "Q"
    for idx in t_list:
        res = res + "_" + str(idx) 
    return res

def SubsMoments(G, zm=[]):
    moments=dict()
    for idxL in G.lines:
        moments[idxL] = G.lines[idxL].momenta.SetZeros(zm)
    return moments 

def SubsExtMomenta(G, zm):
    
    ext_momenta_atom = FindFreeMomenta(G)
    ext_momenta = FindExtMomenta(G).string
    zm2=[rggrf.Momenta(string="%s-%s" %(ext_momenta,ext_momenta_atom)),]
    moments=SubsMoments(G, zm+zm2)
    return (moments, ext_momenta, ext_momenta_atom, zm+zm2)

def FindDiffList(G, moments, ext_momenta_atom, degree):
    ext_moment_path=list()
    nodes_in_path = set()
    for idxL in G.internal_lines:
        if ext_momenta_atom in moments[idxL].dict.keys() :
            ext_moment_path.append((idxL,"L"))
            nodes_in_path = nodes_in_path |  set(G.lines[idxL].Nodes())
#            print idxL, moments[idxL].string , ext_moment_path, nodes_in_path
        
    for idxN in nodes_in_path:
        if  G.nodes[idxN].type in [2,4] : # nodes with two fields
            ext_moment_path.append((idxN,"N"))
            
    t_sel = [i for i in rggrf.utils.xSelections(ext_moment_path,degree)]
# TODO: возможно стоит сделать так чтобы [1,2] и [2,1] считались всместе 
    return t_sel


def K(arg, **kwargs):
    def sum(list_):
        res = 0
        for idx in list_:
            res = res + idx
        return res
            
    if isinstance(arg, rggrf.roperation.R1) :
        res = 0
        r1 = arg 
        dim = r1.terms[0].ct_graph.dim
        if dim == 2:
            res = K0(arg, **kwargs) + sum(K1(arg, **kwargs))+ sum(K2(arg, **kwargs))
        elif dim == 0:
            res = K0(arg)
        else : 
            r1.terms[0].ct_graph.GenerateNickel()
            raise ValueError , "unknown graph dim %s,%s " %(r1.terms[0].ct_graph.dim, r1.terms[0].ct_graph.nickel)
        
        return -res # KR' for subgraphs should have "-"
    else:
        raise TypeError , "unknown type for K operation %s" %type(arg)
    
def K0(arg, **kwargs):
    if isinstance(arg,rggrf.roperation.R1):
        res = 0
        r1 = arg 
        for r1term in r1.terms:
            res = res + K0(r1term, **kwargs)
        return res  
    elif isinstance(arg, rggrf.roperation.R1Term) :
        r1term = arg
        ctgraph = r1term.ct_graph
#        print "K0_t ",  ctgraph.internal_nodes
        ctgraph.GenerateNickel()
#        print "K0 ", ctgraph.nickel, ctgraph.dim , ctgraph.internal_nodes
        
        if "zero_moments" in kwargs:
            zm = kwargs["zero_moments"]
        else:
            zm=[]
        for idxL in ctgraph.external_lines:
            zm.append(ctgraph.lines[idxL].momenta)
        res=1
        for idxL in ctgraph.internal_lines:
            curline = ctgraph.lines[idxL]
            prop = ctgraph.model.line_types[curline.type]["propagator"](momenta=curline.momenta.SetZeros(zm))
            for idxD in curline.dots:
                for idx in range(curline.dots[idxD]):
                    prop = ctgraph.model.dot_types[idxD]["action"](propagator=prop)
            res = res*prop
            
        for idxN in ctgraph.internal_nodes:
            curnode = ctgraph.nodes[idxN]
            moment=dict()
            for idx in range(len(curnode.lines)):
                if ctgraph.lines[curnode.lines[idx]].end == idxN :
                    moment["moment%s"%idx] = ctgraph.lines[curnode.lines[idx]].momenta
                else :
                    moment["moment%s"%idx] = - ctgraph.lines[curnode.lines[idx]].momenta

#            print ctgraph.nodes.keys(), r1term.subgraphs, idxN, r1term.subgraph_map
            if idxN in r1term.subgraph_map:
                f_arg = rggrf.roperation.R1(r1term.subgraphs[r1term.subgraph_map[idxN]].Clone(zero_moments=zm))
            else:
                f_arg = None
            factor = ctgraph.model.node_types[curnode.type]["Factor"](f_arg,**moment)
# дифференцирования вершин?            
            res = res * factor
             
#        print "res K0 %s" %res
        return res
        
            
        
    else:
        raise TypeError , "unknown type for K0 operation %s" %arg

def K_n(r1_term, diff_list=[], **kwargs):
    if isinstance(r1_term, rggrf.roperation.R1Term):
        if len(diff_list)>0:
            _N = len(diff_list[0])
        else:
            raise ValueError, "empty diff_list! "
        r1term=r1_term
        ctgraph=r1term.ct_graph
        
        if "zero_moments" in kwargs:
            zm = kwargs["zero_moments"]
        else:
            zm=[]
            
        (moments, ext_momenta, ext_momenta_atom,  zm) = SubsExtMomenta(ctgraph, zm)
#        print "K2 ", ctgraph.nickel, ctgraph.dim , ctgraph.internal_nodes , diff_list 
        res=[]
        for cur_diff in diff_list:
            t_res=1
            strech = var('L_temp_strech')
            for idxL in ctgraph.internal_lines:
                curline = ctgraph.lines[idxL]
                prop = ctgraph.model.line_types[curline.type]["propagator"](momenta=moments[idxL])
                for idxD in curline.dots:
                    for idx in range(curline.dots[idxD]):
                        prop = ctgraph.model.dot_types[idxD]["action"](propagator=prop)
                prop = rggrf.Streching(prop, rggrf.Momenta(string=ext_momenta_atom).sympy, strech)
                for idx in range(cur_diff.count((idxL,"L"))):
                    prop = prop.diff(strech)
                
                
                t_res = t_res*prop
                
            for idxN in ctgraph.internal_nodes:
                curnode = ctgraph.nodes[idxN]
                moment=dict()
                for idx in range(len(curnode.lines)):
                    if ctgraph.lines[curnode.lines[idx]].end == idxN :
                        moment["moment%s"%idx] = ctgraph.lines[curnode.lines[idx]].momenta
                    else :
                        moment["moment%s"%idx] = - ctgraph.lines[curnode.lines[idx]].momenta
    
    #            print ctgraph.nodes.keys(), r1term.subgraphs, idxN, r1term.subgraph_map
                factor_diff=0
                if idxN in r1term.subgraph_map:
                    f_arg = rggrf.roperation.R1(r1term.subgraphs[r1term.subgraph_map[idxN]].Clone(zero_moments=zm))
                    for idx in cur_diff: 
                        if idx[0] in r1term.subgraphs[r1term.subgraph_map[idxN]].internal_lines :
                            factor_diff=factor_diff +1
                        
                else:
                    f_arg = None
                factor = ctgraph.model.node_types[curnode.type]["Factor"](f_arg,**moment)
# дифференцирования вершин?
                factor = rggrf.Streching(factor, rggrf.Momenta(string=ext_momenta_atom).sympy, strech)             
                for idx in range(cur_diff.count((idxN,"N")) + factor_diff):
                    factor = factor.diff(strech)
                
            
                t_res = t_res * factor
# TODO: ПРОВЕРИТЬ!!! квадрат импульса должен быть в терминах Q охватывающих подграфов.
#            t_res = rggrf.Momenta(string=ext_momenta_atom).sympy*rggrf.Momenta(string=ext_momenta_atom).sympy*t_res.subs(rggrf.Momenta(string=ext_momenta_atom).sympy,0)
#            print "K2 substituing %s = %s" %(ext_momenta_atom,ext_momenta) 
            t_res = Rational(1, Factorial(_N))*rggrf.ExpandScalarProdAsVectors(t_res.subs(strech,0), 
                        rggrf.Momenta(string=ext_momenta_atom), 
                        rggrf.Momenta(string=ext_momenta))
            
            res.append(t_res) 
#        print "res K2 %s" %res
        return res
    else:
        raise TypeError , "unknown type for K_n operation %s " %type(arg)
    

def K1(arg, diff_list=[], **kwargs):
        
    if isinstance(arg,rggrf.roperation.R1):
        res = 0
        r1 = arg
        if "zero_moments" in kwargs:
            zm = kwargs["zero_moments"]
        else:
            zm=[]
        
        
        t_graph = r1.terms[0].ct_graph
        (moments, ext_momenta, ext_momenta_atom, zm) = SubsExtMomenta(t_graph, zm)
        t_diff_list = FindDiffList(t_graph, moments, ext_momenta_atom, 1)
#        print "K2 R1 ", t_diff_list, ext_momenta_atom
 
        res = K1(r1.terms[0], t_diff_list, **kwargs) 
        for r1term in r1.terms[1:]:
            t_res = K1(r1term, t_diff_list, **kwargs)
            if len(res) <> len(t_res):
                raise ValueError, "K1 operation on different terms returns lists with different length  %s %s" %(len(res),len(t_res))
            for idx in range(len(res)):
                res[idx] = res[idx] + t_res[idx]
        return res  
    
    
    
    elif isinstance(arg, rggrf.roperation.R1Term) :
#TODO: выделить общий код в отдельную функцию
        return  K_n( arg , diff_list, **kwargs)
                
def K2(arg, diff_list=[], **kwargs):
    
    if isinstance(arg,rggrf.roperation.R1):
        res = 0
        r1 = arg
        if "zero_moments" in kwargs:
            zm = kwargs["zero_moments"]
        else:
            zm=[]
        
        
        t_graph = r1.terms[0].ct_graph
        (moments, ext_momenta, ext_momenta_atom, zm) = SubsExtMomenta(t_graph, zm)
        t_diff_list = FindDiffList(t_graph, moments, ext_momenta_atom, 2)
#        print "K2 R1 ", t_diff_list, ext_momenta_atom
 
        res = K2(r1.terms[0], t_diff_list, **kwargs) 
        for r1term in r1.terms[1:]:
            t_res = K2(r1term, t_diff_list, **kwargs)
            if len(res) <> len(t_res):
                raise ValueError, "K2 operation on different terms returns lists with different length  %s %s" %(len(res),len(t_res))
            for idx in range(len(res)):
                res[idx] = res[idx] + t_res[idx]
        return res      
    elif isinstance(arg, rggrf.roperation.R1Term) :
        return  K_n( arg , diff_list, **kwargs)
    else:
        raise TypeError , "unknown type for K2 operation %s " %type(arg)


def ExpandScalarProdsAndPrepare(expr):
    import re as regex
    atoms = expr.atoms()
    t_expr = expr
    for atom in atoms:
        reg = regex.match("^(.+)x(.+)$",str(atom))
        if reg :
            atom1 = var(reg.groups()[0])
            atom2 = var(reg.groups()[1])
            t_expr = t_expr.subs(atom,atom*atom1*atom2)
    #Prepare p=1, tau=1
    p=var('p')
    tau=var('tau')
    t_expr = t_expr.subs(p,1).subs(tau,1)
    return t_expr            

           
# model initialization
phi3=rggrf.Model("phi3")

# definition of line types (1 line type)
phi3.AddLineType(1, propagator=propagator, directed=0)

# definition of node types

#External Node always have number 0 and no Lines requirement
phi3.AddNodeType(0, Lines=[], Factor=external_node_factor,
                 gv={"color": "red"}) 
# phi3 node
phi3.AddNodeType(1, Lines=[1, 1, 1], Factor=triple_node_factor)

# nodes from Sigma subgraphs inf counterterms graphs
phi3.AddNodeType(2, Lines=[1, 1], Factor=double_node_factor)

# Nodes with K operation (Lines definition should much to one of 
# subgraphs definitions)

#TODO: generate such nodes automatically when adding subgraph types 
phi3.AddNodeType(3, Lines=[1, 1, 1], Factor=K, gv={"color": "blue"})
phi3.AddNodeType(4, Lines=[1, 1], Factor=K, gv={"color": "blue"})

# relevant subgraph types
phi3.AddSubGraphType(1, Lines=[1, 1, 1], dim=0, K_nodetypeR1=3)
phi3.AddSubGraphType(2, Lines=[1, 1], dim=2, K_nodetypeR1=4)

# definition of dots
phi3.AddDotType(1, dim=2, action=dot_action, gv={"penwidth":"3"})

