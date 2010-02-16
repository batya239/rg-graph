#!/usr/bin/python
# -*- coding:utf8
import sys
from sympy import *
import rggraph_static as rggrf
#import pydot
import copy

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    filename = "moment"

var('p tau p1')

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
            res = K0(arg, **kwargs) + sum(K2(arg, **kwargs))
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
        ctgraph.GenerateNickel()
        print "K0 ", ctgraph.nickel, ctgraph.dim , ctgraph.internal_nodes
        
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
             
        print "res K0 %s" %res
        return res
        
            
        
    else:
        raise TypeError , "unknown type for K0 operation %s" %arg

def xselections(items, n):
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for ss in xselections(items, n-1):
                yield [items[i]]+ss



def K2(arg, diff_list=[], **kwargs):
    
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
    
    def FindDiffList(G, moments, ext_momenta_atom):
        ext_moment_path=list()
        nodes_in_path = set()
        for idxL in G.internal_lines:
            if ext_momenta_atom in moments[idxL].dict.keys() :
                ext_moment_path.append((idxL,"L"))
                nodes_in_path = nodes_in_path |  set(G.lines[idxL].Nodes())
            print idxL, moments[idxL].string , ext_moment_path, nodes_in_path
            
        for idxN in nodes_in_path:
            if  G.nodes[idxN].type in [2,4] : # nodes with two fields
                ext_moment_path.append((idxN,"N"))
                
        t_sel = [i for i in xselections(ext_moment_path,2)]
# TODO: возможно стоит сделать так чтобы [1,2] и [2,1] считались всместе 
        return t_sel
    
    if isinstance(arg,rggrf.roperation.R1):
        res = 0
        r1 = arg
        if "zero_moments" in kwargs:
            zm = kwargs["zero_moments"]
        else:
            zm=[]
        
        
        t_graph = r1.terms[0].ct_graph
        (moments, ext_momenta, ext_momenta_atom, zm) = SubsExtMomenta(t_graph, zm)
        t_diff_list = FindDiffList(t_graph, moments, ext_momenta_atom)
        print "K2 R1 ", t_diff_list, ext_momenta_atom
 
        res = K2(r1.terms[0], t_diff_list, **kwargs) 
        for r1term in r1.terms[1:]:
            t_res = K2(r1term, t_diff_list, **kwargs)
            if len(res) <> len(t_res):
                raise ValueError, "K2 operation on different terms returns lists with different length  %s %s" %(len(res),len(t_res))
            for idx in range(len(res)):
                res[idx] = res[idx] + t_res[idx]
        return res  
    
    
    
    elif isinstance(arg, rggrf.roperation.R1Term) :
        
        r1term=arg
        ctgraph=r1term.ct_graph
        
        if "zero_moments" in kwargs:
            zm = kwargs["zero_moments"]
        else:
            zm=[]
            
        (moments, ext_momenta, ext_momenta_atom,  zm) = SubsExtMomenta(ctgraph, zm)
        print "K2 ", ctgraph.nickel, ctgraph.dim , ctgraph.internal_nodes , diff_list 
        res=[]
        for cur_diff in diff_list:
            t_res=1
            for idxL in ctgraph.internal_lines:
                curline = ctgraph.lines[idxL]
                prop = ctgraph.model.line_types[curline.type]["propagator"](momenta=moments[idxL])
                for idxD in curline.dots:
                    for idx in range(curline.dots[idxD]):
                        prop = ctgraph.model.dot_types[idxD]["action"](propagator=prop)
                for idx in range(cur_diff.count((idxL,"L"))):
                    prop = prop.diff(rggrf.Momenta(string=ext_momenta_atom).sympy)
                
                
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
                for idx in range(cur_diff.count((idxN,"N")) + factor_diff):
                    factor = factor.diff(rggrf.Momenta(string=ext_momenta_atom).sympy)
                
            
                t_res = t_res * factor
# TODO: квадрат импульса должен быть в терминах Q охватывающих подграфов.
#            t_res = rggrf.Momenta(string=ext_momenta_atom).sympy*rggrf.Momenta(string=ext_momenta_atom).sympy*t_res.subs(rggrf.Momenta(string=ext_momenta_atom).sympy,0)
            t_res = rggrf.Momenta(string=ext_momenta).sympy*rggrf.Momenta(string=ext_momenta).sympy*t_res.subs(rggrf.Momenta(string=ext_momenta_atom).sympy,0)
            res.append(t_res) 
        print "res K2 %s" %res
        return res
    else:
        raise TypeError , "unknown type for K2 operation %s " %type(arg)

            

phi3=rggrf.Model("phi3")
phi3.AddLineType(1, propagator=propagator, directed=0)

phi3.AddNodeType(0, Lines=[], Factor=external_node_factor,
                 gv={"color": "red"})  #External Node
phi3.AddNodeType(1, Lines=[1, 1, 1], Factor=triple_node_factor)
phi3.AddNodeType(2, Lines=[1, 1], Factor=double_node_factor) # nodes from Sigma subgraphs
phi3.AddNodeType(3, Lines=[1, 1, 1], Factor=K, gv={"color": "blue"})
phi3.AddNodeType(4, Lines=[1, 1], Factor=K, gv={"color": "blue"})


phi3.AddSubGraphType(1, Lines=[1, 1, 1], dim=0, K_nodetypeR1=3)
phi3.AddSubGraphType(2, Lines=[1, 1], dim=2, K_nodetypeR1=4)

phi3.AddDotType(1, dim=2, action=dot_action, gv={"penwidth":"3"})
print phi3.line_types[1]["propagator"](momenta=rggrf.Momenta(string="+p-q1+q2"))

print phi3

G = rggrf.Graph(phi3)
G.LoadLinesFromFile(filename)
G.lines[5].dots[1] = 1
G.DefineNodes({})

for idxN in G.nodes:
    print "idxN=",idxN, "type=", G.nodes[idxN].type, "Lines=",G.nodes[idxN].lines
for idxL in G.lines:
    print "idxL=",idxL, "type=", G.lines[idxL].type, "In=",G.lines[idxL].start, "Out=",G.lines[idxL].end , "Moment=",G.lines[idxL].momenta
    
G.SaveAsPNG("graph.png") 
print G.external_lines
print G.internal_lines
print

print G


G.FindSubgraphs()


    
r1 = rggrf.roperation.R1(G)

        
G.GenerateNickel()
print G.nickel
G.SaveAsPNG("graph_and_subgraphs.png")
r1.SaveAsPNG("R1.png")

if len(G.external_lines) == 2:
    tmp = K2(r1)
    print tmp , "\n\n"
    pretty_print(tmp)
elif len(G.external_lines) == 3:
    tmp = K0(r1) 
    print tmp , "\n\n"
    pretty_print(tmp)
    