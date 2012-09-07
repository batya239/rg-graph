#!/usr/bin/python
# -*- coding: utf8
import sys
from dummy_model import _phi3,_phi4

from graphs import Graph
import subgraphs
import copy
from comb import xUniqueCombinations

def Prepare(graph, model):
    model.SetTypes(graph)
    graph.FindSubgraphs(model)

def internal_lines(node):
    res=[]
    for line in node.Lines():
        if line.isInternal():
            res.append(line)
    return res

def nodes2process(line,stopnodes):
    res=[]
    if line.start not in stopnodes:
        res.append(line.start)
    if line.end not in stopnodes:
        res.append(line.end)
    return res

def Tree2V(graph,node1,node2):
    stopnodes=[node1,node2]
    trees=[]
    for line in internal_lines(node1):
        stop=False
        tree=set([line])
        while not stop:
            stop=True
            n2p=list()
            for line in tree:
                n2p+=nodes2process(line,stopnodes)
            if len(n2p):
                stop=False
                for node in n2p:
                    tree=tree|set(internal_lines(node))
                    stopnodes.append(node)
        if frozenset(tree) not in trees:
            trees.append(frozenset(tree))
    return trees
    
def NLoopTree(tree):
    nodes=set([])
    for line in tree:
        nodes=nodes|set(line.Nodes())
    return len(tree)-len(nodes)+1

def add_trees(trees,idxs):
    res=list()
    for i in idxs:
        res+=trees[i]
    return res


def combine_trees(trees):
    if len(trees)<=2:
        return [trees]
    else:
        res=list()
        for n in range(1,len(trees)):
            for comb in xUniqueCombinations(range(len(trees)),n):
                rest=list(set(range(len(trees)))-set(comb))
                tree1=add_trees(trees,comb)
                tree2=add_trees(trees,rest)
                res.append((tree1,tree2))
        return res



  
def check2VI(graph):
     int_nodes=[node for node in graph.xInternalNodes()]
     int_lines=set([line for line in graph.xInternalLines()])
     r2VI=False
     mintree=1000000
     minnodes=None
     for nodes in xUniqueCombinations( int_nodes, 2):
#         print
#         print nodes
         trees=Tree2V(graph,nodes[0],nodes[1])
#         print trees, mintree
#         if len(trees)<>1:
         for trees_ in combine_trees(trees):

             if len(trees_)==2:
                 r2VI=False
#                 print map(NLoopTree, trees_)
                 maxcurtree=max(map(NLoopTree, trees_))
    #             print nodes, trees
                 if maxcurtree<mintree:
                     mintree=maxcurtree
                     minnodes=nodes

#     print minnodes, "max subdiagramm = ",mintree
     return (minnodes, mintree )

phi4=_phi4('dummy')

g1=Graph(sys.argv[1])
name=str(g1.GenerateNickel())
#print name
g2=Graph(name)

Prepare(g2,phi4)

if int(sys.argv[2])==-1:
    subgraphs.RemoveTadpoles(g2)
    if len(g2._subgraphs)==0:
       print name
else:
    if len(g2._subgraphs)<>0:
         (nodes,maxtree)=check2VI(g2)
#         print nodes, maxtree
         if maxtree > int(sys.argv[2]):
             subs_toremove=subgraphs.DetectSauseges(g2._subgraphs)
             g2.RemoveSubgaphs(subs_toremove)
             subgraphs.RemoveTadpoles(g2)

             print "%s %s maxtree=%s #subgraphs=%s %s"%(name,nodes,maxtree, len(g2._subgraphs), g2._subgraphs)


