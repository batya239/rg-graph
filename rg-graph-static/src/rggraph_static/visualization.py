#!/usr/bin/python
# -*- coding: utf8

from model import Model
from graph import *
import pydot



def Graph2dot(G):
    strdot = "digraph G {\n"
    #adding Nodes
    for idxN in G.Nodes:
        strdot=strdot + str(idxN) + "000 [ label=\"" + str(idxN) + "\""
        if "Graphviz" in G.model.NodeTypes[G.Nodes[idxN].Type]: 
            strdot = strdot + ", " + G.model.NodeTypes[G.Nodes[idxN].Type]["Graphviz"]
        strdot = strdot + "];\n"
    #adding Lines
    for idxL in G.Lines:
        strdot = strdot + str(G.Lines[idxL].In) + "000 -> " + str(G.Lines[idxL].Out) + "000 [label=\"" + G.Lines[idxL].Momenta + " (" + str(idxL) + ")\""
        if "Graphviz" in G.model.LineTypes[G.Lines[idxL].Type]: 
            strdot = strdot + ", " + G.model.LineTypes[G.Lines[idxL].Type]["Graphviz"]
        strdot = strdot + "];\n"
    strdot = strdot + "}\n"
    return strdot

def GraphSubgraph2dot(G):
    dot=pydot.Dot(graph_type='digraph')
    s1=pydot.Cluster('s',label='graph')
    for idxN in G.Nodes:
        if "gv" in  G.model.NodeTypes[G.Nodes[idxN].Type]:
            s1.add_node( pydot.Node(str(idxN)+"s",label=str(idxN),**G.model.NodeTypes[G.Nodes[idxN].Type]["gv"]))
        else:
            s1.add_node( pydot.Node(str(idxN)+"s",label=str(idxN)))
        
    for idxL in G.Lines:
        if "gv" in  G.model.LineTypes[G.Lines[idxL].Type]:
            s1.add_edge(pydot.Edge( str(G.Lines[idxL].In)+"s", 
                                str(G.Lines[idxL].Out)+"s", 
                                label = " (%s) %s" %(idxL, G.Lines[idxL].Momenta),**G.model.LineTypes[G.Lines[idxL].Type]["gv"]) )
        else:
            s1.add_edge(pydot.Edge( str(G.Lines[idxL].In)+"s", 
                                str(G.Lines[idxL].Out)+"s", 
                                label = " (%s) %s" %(idxL, G.Lines[idxL].Momenta)) )
    dot.add_subgraph(s1)
    for idxS in range(len(G.subgraphs)):
        subname="s%s" %idxS
        sub=pydot.Cluster(subname, label="subgraph %s" %idxS)
        curS=G.subgraphs[idxS]
        for idxN in curS.Nodes:
            if "gv" in  G.model.NodeTypes[curS.Nodes[idxN].Type]:
                sub.add_node( pydot.Node(str(idxN)+subname, label=str(idxN),
                                **G.model.NodeTypes[curS.Nodes[idxN].Type]["gv"]))
            else:
                sub.add_node( pydot.Node(str(idxN)+subname, label=str(idxN)))
        for idxL in curS.Lines:
            if "gv" in  G.model.LineTypes[curS.Lines[idxL].Type]:
                sub.add_edge(pydot.Edge( str(curS.Lines[idxL].In)+subname, 
                                str(curS.Lines[idxL].Out)+subname, 
                                label = " (%s) %s" %(idxL, curS.Lines[idxL].Momenta), 
                                **G.model.LineTypes[curS.Lines[idxL].Type]["gv"]) )
            else:
                sub.add_edge(pydot.Edge( str(curS.Lines[idxL].In)+subname, 
                                str(curS.Lines[idxL].Out)+subname, 
                                label = " (%s) %s" %(idxL, curS.Lines[idxL].Momenta)) )
        dot.add_subgraph(sub)    
        
        
    
    return dot
    