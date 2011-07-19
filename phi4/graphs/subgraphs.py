#!/usr/bin/python
# -*- coding:utf8

from store import _Nodes, _Lines

from comb import xUniqueCombinations

def Dim(subgraph,model):
    """ Calculate dimension of subgraph
         subgraph is list of its internal lines
    """
    _lines_store=_Lines()
    dim=0
    nodes_set=set()
    for idx in subgraph:
        line=_lines_store.Get(idx)
        dim+=line.Dim(model)
        nodes_set=nodes_set|set(line.Nodes())
    for node in nodes_set:
        dim+=node.Dim(model)
    dim+=model.space_dim*NLoopSub(subgraph)
    return dim

def NLoopSub(subgraph):
    return len(subgraph)-len(InternalNodes(subgraph))+1

def InternalNodes(subgraph):
    nodes=set()
    _lines_storage=_Lines()
    _nodes_storage=_Nodes()
    for idxL in subgraph:
        line = _lines_storage.Get(idxL)
        nodes=nodes|set(line.Nodes())
    return nodes

def FindExternal(subgraph):
    all_nodes=set()
    all_lines=set()
    for node in InternalNodes(subgraph):
        for line in node.Lines():
            all_nodes=all_nodes|set(line.Nodes())
            all_lines=all_lines|set([line.idx()])
#nodes as objects lines as links. rewrite?
    return (all_nodes-InternalNodes(subgraph), all_lines-set(subgraph))

def ToEdges(subgraph):
    (extnodes,extlines)=FindExternal(subgraph)
    res=[]
    _lines_storage=_Lines()
    for idxL in subgraph:
        line=_lines_storage.Get(idxL)
        res.append([x.idx() for x in line.Nodes()])
    for idxL in extlines:
        line=_lines_storage.Get(idxL)
        (node1,node2)=line.Nodes()
        if node1 in extnodes and node2 not in extnodes:
            res.append([-1,node2.idx()])
        elif node1 not in extnodes and node2 in extnodes:
            res.append([node1.idx(),-1]) 
        elif node1 not in extnodes and node2 not in extnodes:
# на самом деле после стягивания такого подграфа возникает 
#  головастик
            res.append([node1.idx(),-1]) 
            res.append([-1,node2.idx()])
        else:
            raise ValueError,  "Invalid subgraph"
    return res

def sub2objects(subgraph):
    _lines_store=_Lines()
    return [_lines_store.Get(x) for x in subgraph]
def isSubgraph1PI(subgraph):
    res = True
    subobj=sub2objects(subgraph)
    for line in subobj:
        reduced=list(set(subobj)-set([line]))
        _nodes=set(reduced[0].Nodes())
        flag=True
        while flag:
            flag=False
            for node in _nodes:
                for line in node.Lines():
                    if (line in reduced)and len(_nodes & set(line.Nodes()))==1:
                        _nodes = _nodes | set(line.Nodes())
                        flag=True
        if _nodes <> InternalNodes(subgraph):
            res=False
            break
    return res
        

def FindSubgraphs(graph,model):
    _subgraphs=[]
    intLines=[x.idx() for x in graph.xInternalLines()]
    for idx in range(2, len(intLines)):
        candidates=[i for i in xUniqueCombinations(intLines,idx)]
        for sub in candidates:
            print graph._lines
            print sub
            print Dim(sub,model), isSubgraph1PI(sub)
            if Dim(sub,model)>=0 and isSubgraph1PI(sub):
                _subgraphs.append(sub)
    return _subgraphs