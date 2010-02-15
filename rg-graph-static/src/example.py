#!/usr/bin/python
# -*- coding:utf8
import sys
from sympy import *
import rggraph_static as rggrf
import pydot

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    filename = "moment"

var('p tau p1')

def propagator(**kwargs):
    var('tau')
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
    var('tau')
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
        for r1term in r1.terms:
            res = res + K(r1term)
        return -res # KR' for subgraphs should have "-"
    elif isinstance(arg, rggrf.roperation.R1Term) :
        r1term = arg
        ctgraph = r1term.ct_graph
        ctgraph.GenerateNickel()
        print "K " , ctgraph.nickel , ctgraph.dim ,ctgraph.internal_nodes       
        if ctgraph.dim == 2 : 
            return K0(arg) + sum(K2(arg))
        elif ctgraph.dim == 0 :
            return K0(arg)
        else : 
            ctgraph.GenerateNickel()
            raise ValueError , "unknown graph dim %s,%s " %(ctgraph.dim,ctgraph.nickel)
    else:
        raise TypeError , "unknown type for K operation %s" %type(arg)
    
def K0(arg, **kwargs):
    if isinstance(arg,rggrf.roperation.R1):
        res = 0
        r1 = arg 
        for r1term in r1.terms:
            res = res + K0(r1term)
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

            print ctgraph.nodes.keys(), r1term.subgraphs, idxN, r1term.subgraph_map
            if idxN in r1term.subgraph_map:
                f_arg = rggrf.roperation.R1(r1term.subgraphs[r1term.subgraph_map[idxN]].Clone(zero_moments=zm))
            else:
                f_arg = None
            factor = ctgraph.model.node_types[curnode.type]["Factor"](f_arg,**moment)
# дифференцирования вершин?            
            res = res * factor 
        
        return res
        
            
        
    else:
        raise TypeError , "unknown type for K0 operation %s" %arg

def K2(arg, **kwargs):
    if not isinstance(arg,rggrf.roperation.R1):
        res = 0
        r1 = arg
        res = K2(r1.terms[0]) 
        for r1term in r1.terms[1:]:
            t_res = K2(r1term)
            if len(res) <> len(t_res):
                raise ValueError, "K2 operation on different terms returns lists with different length  %s %s" %(len(res),len(t_res))
            for idx in range(len(res)):
                res[idx] = res[idx] + t_res[idx]
        return res  
    elif isinstance(arg, rggrf.roperation.R1Term) :
        
        
        pass
    else:
        raise TypeError , "unknown type for K0 operation %s" %type(arg)

            

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
G.lines[6].dots[1] = 1
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

print K0(r1)
    