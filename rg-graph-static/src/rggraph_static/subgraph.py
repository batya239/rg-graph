#!/usr/bin/python
# -*- coding: utf8

#from model import Model
from graph import *

def FindSubgraphType(G, subgraph, subgraph_types=False):
    if subgraph_types == False:
        subgraph_types = G.model.subgraph_types
    sub_type = []
    sub_nodes=FindSubgraphNodes(G,subgraph)
    for idxL in FindExternalLines(G, subgraph):
        sub_type.append(G.lines[idxL].type)
        if len(set(G.lines[idxL].Nodes())&set(sub_nodes)) == 2:
            sub_type.append(G.lines[idxL].type)
    sub_type.sort()
    res_subgraph_type = -1
    res_divergence = -1
    for idxST in subgraph_types:
        if idxST <> 0:
            tmpSGType = list(subgraph_types[idxST]["Lines"])
            tmpSGType.sort()
            #print subtype,tmpSGType
            if sub_type == tmpSGType: 
                res_subgraph_type = idxST
                res_divergence = subgraph_types[idxST]["dim"] 
                break
    subgraph_dot_count=SubgraphDotCount(G, subgraph)
    for idxD in subgraph_dot_count:
        res_divergence=res_divergence-subgraph_dot_count[idxD]*G.model.dot_types[idxD]["dim"]
    
    return (res_subgraph_type,res_divergence)

def FindSubgraphNodes(G, subgraph):
    res = set([])
    for idxL in subgraph:
        res = res | set(G.lines[idxL].Nodes())
    return res

def FindExternalLines(G, subgraph):
    all_lines = set([])
    for idxN in FindSubgraphNodes(G, subgraph):
        all_lines = all_lines | set(G.nodes[idxN].lines)
    return all_lines-set(subgraph)

def IsSubgraph1PI(G, subgraph):
    res = True
    for idxL in subgraph:
        rsubgraph = set(subgraph) - set([idxL,])
#            print "\n---", rsubgraph, G.Lines[list(rsubgraph)[0]].Nodes()
        nodes = set(G.lines[list(rsubgraph)[0]].Nodes())
        
        flag = 0
        while(flag == 0):
            flag = 1
            for idxN in nodes:
                for idxNL in G.nodes[idxN].lines:
                    if idxNL in rsubgraph:
                        if len(nodes & set(G.lines[idxNL].Nodes())) < 2:
                            nodes = nodes | set(G.lines[idxNL].Nodes())
                            flag = 0
        if nodes <>  FindSubgraphNodes(G, subgraph):
            res = False
    return res
                     
def CreateSubgraph(G, subgraph):
    graph_node_types=G.GetNodesTypes()
    subgraph_nodes=FindSubgraphNodes(G, subgraph)
    for idxN in graph_node_types:
        if idxN not in subgraph_nodes:
            graph_node_types[idxN]=0  # External node
            
    sub=Graph(G.model)
    for idxL in subgraph:
        sub.AddLine(idxL, G.lines[idxL])
#        print subgraph, subgraphNodes, FindExternalLines(G, subgraph)
    for idxL in FindExternalLines(G, subgraph):

# внешняя линия соединяет вершины принадлежащие подграфу:
# чтобы интерпретировать ее как внешнюю для подграфа необходимо ее 
# разорвать и обрывки линий прицепить к некоей фиктивной внешней
# вершине. типичный пример четереххвостый подграф в арбузе.

        if len(set(G.lines[idxL].Nodes())&set(subgraph_nodes)) == 2: 
            
            fake_node=100000
            idxL1=idxL*1000+1
            idxL2=idxL*1000+2
            sub.AddLine(idxL1, Line(G.lines[idxL].type, G.lines[idxL].start, 
                                    fake_node, G.lines[idxL].momenta,
                                    G.lines[idxL].dots))
            
            sub.AddLine(idxL2, Line(G.lines[idxL].type, fake_node, 
                                    G.lines[idxL].end,G.lines[idxL].momenta, 
                                    G.lines[idxL].dots))
            
            if fake_node not in graph_node_types: graph_node_types[fake_node]=0
        else:
            sub.AddLine(idxL, G.lines[idxL])
    sub.DefineNodes(graph_node_types)
    return sub

def SubgraphDotCount(G, subgraph):
    res = dict()
    for idxL in subgraph:
        for idxD in G.lines[idxL].dots:
            if idxD in res:
                res[idxD] = res[idxD] + 1
            else:
                res[idxD] = 1
    return res

def Find(G, subgraph_types):
    """ G -graph
        SubGraphTypes - dict of subgraph types as defined in Model
    """
    def xuniqueCombinations(items, n):
        if n==0: yield []
        else:
            for i in xrange(len(items)):
                for cc in xuniqueCombinations(items[i+1:],n-1):
                    yield [items[i]]+cc
                  
    res=[]
    internal_lines = list(G.internal_lines)
    internal_lines.sort()
    subgraphs = []
    for idx in range(2,len(internal_lines)): # количество внтренних линий подграфа
        subgraphs=subgraphs+[i for i in xuniqueCombinations(internal_lines,idx)]
        
    for idxS in subgraphs:
#        print idxS, FindExternalLines(G, idxS), FindSubgraphType(G,idxS), IsSubgraph1PI(G, idxS)
        (subgraph_type, subgraph_divergence) = FindSubgraphType(G, idxS, subgraph_types) 
        if subgraph_type > 0 and subgraph_divergence >= 0 and IsSubgraph1PI(G, idxS):
            #print idxS, FindExternalLines(G, idxS), FindSubgraphType(G,idxS), IsSubgraph1PI(G, idxS)
            res.append(CreateSubgraph(G, idxS))
    return res
            
        
                
           
    