#!/usr/bin/python
# -*- coding:utf8

from comb import xUniqueCombinations
from copy import copy

class Subgraph:
    def __init__(self,lines_list):
        self._lines=copy(lines_list)

    def __repr__(self):
        return self._lines.__repr__()
    
    def InternalNodes(self):
        if not "_InternalNodes" in self.__dict__:
            nodes=set()
            for line in self._lines:
                nodes=nodes|set(line.Nodes())
            self._InternalNodes=nodes
        return self._InternalNodes

    def Dim(self,model):
        """ Calculate dimension of subgraph
             subgraph is list of its internal lines
        """
        dim=0
        nodes_set=set()
        for line in self._lines:
            dim+=line.Dim(model)
            nodes_set=nodes_set|set(line.Nodes())
        for node in nodes_set:
            dim+=node.Dim(model)
        dim+=model.space_dim*self.NLoopSub()
        return dim

    def NLoopSub(self):
        return len(self._lines)-len(self.InternalNodes())+1


    def FindExternal(self):
        if not "_external" in self.__dict__:
            all_nodes=set()
            all_lines=set()
            for node in self.InternalNodes():
                for line in node.Lines():
                    all_nodes=all_nodes|set(line.Nodes())
                    all_lines=all_lines|set([line])
            self._external = (all_nodes-self.InternalNodes(), all_lines-set(self._lines))
        return self._external

    def CountExtLegs(self):
        """ counts external legs for subgraph. Note: it isn't equal to len(extlines). ex. subgraphs in watermelone
            for selfenergy subgraphs it is the same if we did not taking into account vacuum loops
        """
        extnodes,extlines=self.FindExternal()
        intnodes=self.InternalNodes()
        cnt=0
        for line in extlines:
            for node in line.Nodes():
                if node in intnodes:
                    cnt+=1
        return cnt

    def BorderNodes(self):
        """ border node is internal node that connected to external node
        """
        if not "_border" in self.__dict__:
            extnodes,extlines=self.FindExternal()
            border=set()
            for line in extlines:
                border=border|set(line.Nodes())
            self._border=border-extnodes
        return self._border

    def __len__(self):
        return len(self._lines)

    def linePresent(self,line):
        if line in self._lines:
            return True
        else:
            return False

    def FindTadpoles(self,_subgraphs=None):
	if not "_tadpoles" in self.__dict__:
            intnodes=self.InternalNodes()
            (extnodes,extlines)=self.FindExternal()
            border=self.BorderNodes()
            tadpoles=list()
            for sub in _subgraphs:
                if len(self)>len(sub):
                    """ othewise sub cant be subgraph of sub1
                    """
                    if reduce(lambda x,y: x&y,[(line in self._lines) for line in sub._lines]):
                        """ all lines in sub are in sub1
                        """
                        _border=sub.BorderNodes()
                        if reduce(lambda x,y: x&y,[(node in _border) for node in border]):
                            """ border of sub1 (biger) inside border sub (smaller)
                                this gives us tadpole in sub1 after sub reduced to point
                            """
                            tadpoles.append(sub)
            self._tadpoles=tadpoles
        return self._tadpoles
    

    def ToEdges(self):
        (extnodes,extlines)=self.FindExternal()
        res=[]
        for line in self._lines:
            res.append([x.idx() for x in line.Nodes()])
        for line in extlines:
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

    def isSubgraph1PI(self):
        res = True
        for line in self._lines:
            reduced=list(set(self._lines)-set([line]))
            _nodes=set(reduced[0].Nodes())
            flag=True
            while flag:
                flag=False
                for node in _nodes:
                    for line in node.Lines():
                        if (line in reduced)and len(_nodes & set(line.Nodes()))==1:
                            _nodes = _nodes | set(line.Nodes())
                            flag=True
            if _nodes <> self.InternalNodes():
                res=False
                break
        return res

    def asLinesIdxStr(self):
        res=[x.idx() for x in  self._lines]
        res.sort()
        return reduce(lambda x,y: "%s_%s"%(x,y))
        

def FindSubgraphs(graph,model):
#TODO: FindSubgraphs is SLOW!?
    _subgraphs=[]
    intLines=[x for x in graph.xInternalLines()]
    for idx in range(2, len(intLines)):
        candidates=[Subgraph(i) for i in xUniqueCombinations(intLines,idx)]
        for sub in candidates:
            if sub.Dim(model)>=0 and sub.isSubgraph1PI():
                _subgraphs.append(sub)
    return _subgraphs
