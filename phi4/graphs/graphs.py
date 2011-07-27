#!/usr/bin/python
# -*- coding:utf8

import copy

import nickel

from store import _Lines, _Nodes
from nodes import Node
#from lines import Line



def _find_empty_idx(keys_):
   idx=0
   while idx in keys_:
       idx+=1
   return idx


class Graph:
    def __init__(self,arg):
        self._lines = list()
        self._nodes = list()
        if isinstance(arg,str):
# construct graph from nickel index
            self._from_lines_list(nickel.Nickel(string=arg).edges)
        elif isinstance(arg,list):
# construct graph from edges 
            self._from_lines_list(arg)
        else:
            raise TypeError, "Unsupproted type of argument: %s"%arg

    def _Node(self,idx):
        _nodes_store=_Nodes()
        return _nodes_store.Get(idx)

    def _Line(self,idx):
        _lines_store=_Lines()
        return _lines_store.Get(idx)

    def _from_lines_list(self,list_):
        _nodes_store=_Nodes()
        _lines_store=_Lines()
        _lines_dict=dict()
        _nodes_dict=dict()
        list__=copy.copy(list_)
        list__.sort()
        for line in list__:
            if len(line) == 2:
                for node in line[0:2]:
                    if node not in _nodes_dict.keys():
                        _type=None
                        if node<0:
                            _type=-1 #external node
                        _nodes_dict[node]=_nodes_store.Add(Node(type=_type))
                self._lines.append(self._Node(_nodes_dict[line[0]]).AddLine(_nodes_dict[line[1]]))
                 
            else:
                raise ValueError, "Invalid line %s"%line
        self._nodes=_nodes_dict.values()
                
    def _edges(self):
        res=[]
        for idx in self._lines:
            _nodes=[]
            for node in self._Line(idx).Nodes():
                if (node.type<>None) and (node.type<0) :
                    _nodes.append(-1)
                else:
                    _nodes.append(node.idx())
            res.append(_nodes)
#        res.sort()
        return res
                         
    def GenerateNickel(self):
        self.nickel=nickel.Canonicalize(self._edges())

    def xInternalNodes(self):
        
        for idx in self._nodes:
            node=self._Node(idx)
            if node.isInternal():
                yield node

    def xInternalLines(self):
        
        for idx in self._lines:
            line=self._Line(idx)
            if line.isInternal():
                yield line

    def Lines(self):
        return [self._Line(x) for x in self._lines]
            

    def NLoops(self):
#TODO: rewrite nloops in more efficient way
        return len([x for x in self.xInternalLines()])-len([x for x in self.xInternalNodes()])+1

    def Dim(self, model):

        dim = self.NLoops()*model.space_dim

        for line in self.xInternalLines():
            dim = dim + line.Dim(model)

        for node in self.xInternalNodes():
            dim = dim + node.Dim(model)

        return dim