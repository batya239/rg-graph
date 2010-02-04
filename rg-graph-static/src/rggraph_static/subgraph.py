#!/usr/bin/python
# -*- coding: utf8

#from model import Model
from graph import *

def Find(G, SubGraphTypes):
    """ G -graph
        SubGraphTypes - dict of subgraph types as defined in Model
    """
    def xuniqueCombinations(items, n):
        if n==0: yield []
        else:
            for i in xrange(len(items)):
                for cc in xuniqueCombinations(items[i+1:],n-1):
                    yield [items[i]]+cc
    
    def FindSubgraphNodes(G, subgraph):
        res = set([])
        for idxL in subgraph:
            res = res | set(G.Lines[idxL].Nodes())
        return res
    
    def FindExternalLines(G, subgraph):
        allLines = set([])
        for idxN in FindSubgraphNodes(G, subgraph):
            allLines = allLines | set(G.Nodes[idxN].Lines)
        return allLines-set(subgraph)
    
    def FindSubgraphType(G, subgraph):
        subtype = []
        for idxL in FindExternalLines(G, subgraph):
            subtype.append(G.Lines[idxL].Type)
        subtype.sort()
        res=-1
        for idxST in G.model.SubGraphTypes:
            if idxST <> 0:
                tmpSGType = list(G.model.SubGraphTypes[idxST]["Lines"])
                tmpSGType.sort()
                #print subtype,tmpSGType
                if subtype == tmpSGType: 
                    res = idxST
                    break
        return res
                
    def IsSubgraph1PI(G, subgraph):
        res = True
        for idxL in subgraph:
            rsubgraph = set(subgraph) - set([idxL,])
#            print "\n---", rsubgraph, G.Lines[list(rsubgraph)[0]].Nodes()
            nodes = set(G.Lines[list(rsubgraph)[0]].Nodes())
            
            flag = 0
            while(flag == 0):
                flag = 1
                for idxN in nodes:
                    for idxNL in G.Nodes[idxN].Lines:
                        if idxNL in rsubgraph:
                            if len(nodes & set(G.Lines[idxNL].Nodes())) < 2:
                                nodes = nodes | set(G.Lines[idxNL].Nodes())
                                flag = 0
            if nodes <>  FindExternalLines(G, subgraph):
                res=False
        return res
                         
    def CreateSubgraph(G, subgraph):
        graphNodesTypes=G.GetNodesTypes()
        subgraphNodes=FindSubgraphNodes(G, subgraph)
        for idxN in graphNodesTypes:
            if idxN not in subgraphNodes:
                graphNodesTypes[idxN]=0  # External node
                
        sub=Graph(G.model)
        for idxL in subgraph:
            sub.AddLine(idxL, G.Lines[idxL])
        for idxL in FindExternalLines(G, subgraph):
            if len(set(G.Lines[idxL].Nodes())&set(subgraph)) == 2: # внешняя линия соединяет вершины принадлежащие подграфу
                fakeNode=100000
                idxL1=idxL*1000+1
                idxL2=idxL*1000+2
                sub.AddLine(idxL1, Line(G.Lines[idxL].Type, G.Lines[idxL].In,fakeNode,G.Lines[idxL].Momenta))
                sub.AddLine(idxL2, Line(G.Lines[idxL].Type, fakeNode, G.Lines[idxL].Out,G.Lines[idxL].Momenta))
                if fakeNode not in graphNodesTypes: graphNodesTypes[fakeNode]=0
            else:
                sub.AddLine(idxL, G.Lines[idxL])
        sub.DefineNodes(graphNodesTypes)
        return sub
                 
                 
                
    
    res=[]
    internallines = list(G.InternalLines)
    internallines.sort()
    subgraphs = []
    for idx in range(2,len(internallines)): # количество внтренних линий подграфа
        subgraphs=subgraphs+[i for i in xuniqueCombinations(internallines,idx)]
        
    for idxS in subgraphs:
        if FindSubgraphType(G,idxS)>0 and IsSubgraph1PI(G, idxS):
            print idxS, FindExternalLines(G, idxS), FindSubgraphType(G,idxS), IsSubgraph1PI(G, idxS)
            res.append(CreateSubgraph(G, idxS))
    return res
            
        
                
           
    