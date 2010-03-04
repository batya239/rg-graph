#!/usr/bin/python
# -*- coding: utf8
'''
Created on Feb 17, 2010

@author: mkompan

definition of phi3 model in terms of rggraph_static
'''
from sympy import *
import os
import rggraph_static as rggrf

#definitions of propagators, node factors, dot actions, and K operation 

def propagator(**kwargs):
    tau=var('tau')
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
#        print " -== K0 ==- %s" %r1.terms[0].ct_graph.internal_nodes 
#        for r1term in r1.terms:
#            print r1term.factorization
        for r1term in r1.terms:
#            print r1term.ct_graph.internal_nodes
#            try:
#                res.pprint()
#            except:
#                print res
            t_K0 = K0(r1term, **kwargs)
#            print r1term.ct_graph.internal_nodes
#            t_K0.pprint()
            res = res + t_K0
        return res  
    elif isinstance(arg, rggrf.roperation.R1Term) :
        r1term = arg
        ctgraph = r1term.ct_graph
#        print "K0_t ",  ctgraph.internal_nodes
#        ctgraph.GenerateNickel()
#        print "K0 ", ctgraph.nickel, ctgraph.dim , ctgraph.internal_nodes
        
        if "zero_moments" in kwargs:
            zm = kwargs["zero_moments"]
        else:
            zm=[]
        for idxL in ctgraph.external_lines:
#            print "K0 ext moments: %s, %s" %(idxL,ctgraph.lines[idxL].momenta)
            zm.append(ctgraph.lines[idxL].momenta)
        
        res = rggrf.roperation.Factorized(1,1)
        
        for idxL in ctgraph.internal_lines:
            curline = ctgraph.lines[idxL]
#            print "line before/after zm : %s     %s / %s " %(idxL, curline.momenta, curline.momenta.SetZeros(zm))
            prop = ctgraph.model.line_types[curline.type]["propagator"](momenta=curline.momenta.SetZeros(zm))
            for idxD in curline.dots:
                for idx in range(curline.dots[idxD]):
                    prop = ctgraph.model.dot_types[idxD]["action"](propagator=prop)
#            print "prop = %s" %prop
            if idxL in r1term.factorization:
                res.factor = res.factor * prop
            else:
                res.other = res.other * prop
            
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
                f_arg = rggrf.roperation.R1(r1term.subgraphs[r1term.subgraph_map[idxN]].Clone(zero_moments=zm),r1term.factorization)
            else:
                f_arg = None
            factor = ctgraph.model.node_types[curnode.type]["Factor"](f_arg,**moment)
# дифференцирования вершин?
# TODO: какие-то нетривиальные вершины тоже могут попадать в res_f
            
            res = res * factor
             
#        print "res K0 %s" %res
        return res
        
            
        
    else:
        raise TypeError , "unknown type for K0 operation %s" %arg

def K_n(r1_term, diff_list=[], **kwargs):
#    print "K_n diff_list = %s" %diff_list
#    print "nodes of r1term: %s" %r1_term.ct_graph.internal_nodes
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
#            print "----- cur_diff %s" %cur_diff

            t_res = rggrf.roperation.Factorized(1,1)            
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
                

                if idxL in r1term.factorization:
                    t_res.factor = t_res.factor * prop
                else:
                    t_res.other = t_res.other * prop


                
            for idxN in ctgraph.internal_nodes:
                curnode = ctgraph.nodes[idxN]
                moment=dict()
                for idx in range(len(curnode.lines)):
                    if ctgraph.lines[curnode.lines[idx]].end == idxN :
                        moment["moment%s"%idx] = ctgraph.lines[curnode.lines[idx]].momenta.SetZeros(zm)
                    else :
                        moment["moment%s"%idx] = - ctgraph.lines[curnode.lines[idx]].momenta.SetZeros(zm)
    
    #            print ctgraph.nodes.keys(), r1term.subgraphs, idxN, r1term.subgraph_map
                factor_diff=0
                if idxN in r1term.subgraph_map:
                    f_arg = rggrf.roperation.R1(r1term.subgraphs[r1term.subgraph_map[idxN]].Clone(zero_moments=zm),r1term.factorization)
                    for idx in cur_diff: 
                        if idx[0] in r1term.subgraphs[r1term.subgraph_map[idxN]].internal_lines :
                            factor_diff=factor_diff +1
                        
                else:
                    f_arg = None
                factor = ctgraph.model.node_types[curnode.type]["Factor"](f_arg,**moment)
#                print "start -> %s" %(factor)
#                for tmpidx in zm:
#                    print "--zm: %s %s" %(tmpidx,tmpidx.string)
# дифференцирования вершин?
#                print "strech args -> %s %s %s"  %(factor, rggrf.Momenta(string=ext_momenta_atom).sympy, strech)
                factor.other = rggrf.Streching(factor.other, rggrf.Momenta(string=ext_momenta_atom).sympy, strech)
#                print "strech -> %s" %factor    
#                print "diff count -> %s, %s" %(cur_diff.count((idxN,"N")), factor_diff)                  
                for idx in range(cur_diff.count((idxN,"N")) + factor_diff):
                    factor.other = factor.other.diff(strech)
#                print "res -> %s" %factor
                t_res = t_res * factor
# TODO: ПРОВЕРИТЬ!!! квадрат импульса должен быть в терминах Q охватывающих подграфов.
#            t_res = rggrf.Momenta(string=ext_momenta_atom).sympy*rggrf.Momenta(string=ext_momenta_atom).sympy*t_res.subs(rggrf.Momenta(string=ext_momenta_atom).sympy,0)
#            print "K2 substituing %s = %s" %(ext_momenta_atom,ext_momenta) 

#            t_res_f =  t_res_f
            t_res.other = Rational(1, Factorial(_N)) * rggrf.ExpandScalarProdAsVectors(t_res.other.subs(strech,0), 
                        rggrf.Momenta(string=ext_momenta_atom), 
                        rggrf.Momenta(string=ext_momenta))
#            print "<------>"
#            pretty_print(t_res)
            res.append(t_res) 
#        print "res K2 %s" %res
        return res
    else:
        raise TypeError , "unknown type for K_n operation %s " %type(arg)
    

def K1(arg, diff_list=[], **kwargs):
#    print "K1 diff_list = %s" %diff_list        
    if isinstance(arg,rggrf.roperation.R1):
        res = 0
        r1 = arg
        if "zero_moments" in kwargs:
            zm = kwargs["zero_moments"]
        else:
            zm=[]
        
        
        t_graph = r1.terms[0].ct_graph
        (moments, ext_momenta, ext_momenta_atom, zm) = SubsExtMomenta(t_graph, zm)
#        print ext_momenta, ext_momenta_atom
#        for idx in moments:
#            print "moment %s: %s" %(idx, moments[idx].string)
#        for idx in zm:
#            print "zm: %s" %idx.string 
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
#    print "K2 diff_list = %s" %diff_list
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
#        print " -== K2 ==- %s" %r1.terms[0].ct_graph.internal_nodes 
#        for r1term in r1.terms:
#            print r1term.factorization
            
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

def ExpandScalarProdsAndPrepareFactorized(factorized_expr):
    return rggrf.roperation.Factorized(ExpandScalarProdsAndPrepare(factorized_expr.factor), 
                      ExpandScalarProdsAndPrepare(factorized_expr.other))

def ExpandScalarProdsAndPrepare(expr_):
    if isinstance(expr_,rggrf.roperation.Factorized):
        print "WARNING!!! Factorizied object passed to ExpandScalarProdsAndPrepare"
        expr = expr_.factor*expr_.other
    else:
        expr = expr_ 
    import re as regex
    try:
        atoms = expr.atoms()
    except:
        print "WARNING!!!! %s passed to ExpandScalarProdsAndPrepare" %type(expr)
        return expr
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

phi3.basepath = "~/work/rg-graph/test/"

try:
    os.listdir(rggrf.storage.filesystem.NormalizeBaseName(phi3.basepath))
except:
    raise ValueError, "invalid storage path  %s" %phi3.basepath
phi3.SaveGraph = rggrf.storage.filesystem.SaveGraphAsDict
phi3.LoadGraph = rggrf.storage.filesystem.LoadGraphAsDict

phi3.SaveResults = rggrf.storage.filesystem.SaveResults
phi3.LoadResults = rggrf.storage.filesystem.LoadResults

def ResultWithSd(_dict, nloops, n_eps_series):
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
    for idx in _dict:
        expr = expr + eps**idx*_dict[idx][0]
    expr = expr * t_mnog[nloops-1]
    #print series(expr,eps,0)
    return rggrf.utils.SimpleSeries(expr, eps,0,n_eps_series)

def ResultOldNotation(_dict):
    eps = var('eps')
    expr = 0
    for idx in _dict:
        expr = expr + eps**idx*_dict[idx][0]
     
    #print series(expr,eps,0)
    return expr*2