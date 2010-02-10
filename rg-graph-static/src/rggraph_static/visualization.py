#!/usr/bin/python
# -*- coding: utf8

from model import Model
from graph import *
import pydot



def GraphSubgraph2dot(G):
    dot=pydot.Dot(graph_type='digraph')
    s1=pydot.Cluster('s',label='graph')
    s1=Graph2Cluster(G,"graph")
    dot.add_subgraph(s1)
    for idxS in range(len(G.subgraphs)):
        sub=Graph2Cluster(G.subgraphs[idxS],"sub_%s" %idxS)
        dot.add_subgraph(sub)    

    return dot

def Graph2Cluster(G,name):
    res= pydot.Cluster(name,label="\"%s\"" %name)
    for idxN in G.nodes:
        cur_node=G.nodes[idxN]
        if "gv" in  G.model.node_types[cur_node.type]:
                res.add_node( pydot.Node(str(idxN)+name, label=str(idxN),
                                **G.model.node_types[cur_node.type]["gv"]))
        else:
            res.add_node( pydot.Node(str(idxN)+name, label=str(idxN)))
    for idxL in G.lines:
        cur_line=G.lines[idxL]
        if "gv" in  G.model.line_types[cur_line.type]:
                res.add_edge(pydot.Edge( str(cur_line.start)+name, 
                                str(cur_line.end)+name, 
                                label = " (%s) %s" %(idxL, cur_line.momenta), 
                                **G.model.line_types[cur_line.type]["gv"]) )
        else:
            res.add_edge(pydot.Edge( str(cur_line.start)+name, 
                                str(cur_line.end)+name, 
                                label = " (%s) %s" %(idxL, cur_line.momenta)) )
    return res
    
                    

     

def R12dot(R1):
    dot = pydot.Dot(graph_type='digraph')
    for idxR1 in range(len(R1.terms)):
        cluster = R1Term2Cluster(R1.terms[idxR1],'term_%s' %idxR1)
        dot.add_subgraph(cluster)
    return dot

def R1Term2Cluster(r1_term, name):
    
    res = Graph2Cluster(r1_term.ct_graph, name) 
    for idxN in r1_term.subgraph_map:
        subname="%s_%s" %(name,idxN)
#        print subname,R1Term.SubgraphMap, len(R1Term.subgraphs)
        sub=Graph2Cluster(r1_term.subgraphs[r1_term.subgraph_map[idxN]],subname)
        res.add_subgraph(sub) 
    
    return res
        
        
    